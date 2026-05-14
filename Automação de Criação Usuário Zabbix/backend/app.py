import os
import secrets
import string
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify
from flask_cors import CORS
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from services.zabbix_service import ZabbixService
from services.grafana_service import GrafanaService
from utils.logger import logger, audit_logger

load_dotenv()

app = Flask(__name__)
CORS(app)

ZABBIX_URL = os.getenv("ZABBIX_URL")
ZABBIX_USER = os.getenv("ZABBIX_USER")
ZABBIX_PASS = os.getenv("ZABBIX_PASS")

GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_API_TOKEN = os.getenv("GRAFANA_API_TOKEN")

def generate_complex_password(length=16):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "provisioning-api"})

@app.route('/api/zabbix/groups', methods=['GET'])
def get_zabbix_groups():
    zabbix_svc = ZabbixService(ZABBIX_URL, ZABBIX_USER, ZABBIX_PASS)
    auth_token = None
    try:
        auth_token = zabbix_svc.login()
        groups = zabbix_svc.get_user_groups(auth_token)
        return jsonify({"groups": groups}), 200
    except Exception as e:
        logger.error(f"Error fetching Zabbix groups: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if auth_token:
            try:
                zabbix_svc.logout(auth_token)
            except Exception as logout_err:
                logger.error(f"Error logging out Zabbix: {str(logout_err)}")

@app.route('/api/provision', methods=['POST'])
def provision():
    data = request.json
    
    alias = data.get('alias')
    email = data.get('email')
    name = data.get('name')
    surname = data.get('surname')
    roleid = data.get('roleid')
    usrgrpids = data.get('usrgrpids', [])
    targets = data.get('targets', [])
    
    # Identify the requester (e.g., from IP)
    requester_ip = request.remote_addr or "Unknown IP"
    
    if not targets:
        return jsonify({"error": "No target systems specified"}), 400

    if not all([alias, name, surname, roleid, usrgrpids]):
        return jsonify({"error": "Missing required Zabbix fields"}), 400

    if 'grafana' in targets and not email:
        return jsonify({"error": "Email is required for Grafana"}), 400

    results = {}

    # Zabbix Provisioning
    if 'zabbix' in targets:
        zabbix_svc = ZabbixService(ZABBIX_URL, ZABBIX_USER, ZABBIX_PASS)
        auth_token = None
        try:
            auth_token = zabbix_svc.login()
            if zabbix_svc.check_user_exists(auth_token, alias):
                results['zabbix'] = {"status": "error", "message": "User already exists"}
                audit_logger.warning(f"IP: {requester_ip} | Target: Zabbix | Action: CREATE_USER | Status: FAILED (Already Exists) | Alias: {alias}")
            else:
                complex_pwd = generate_complex_password()
                z_result = zabbix_svc.create_user(auth_token, alias, name, surname, roleid, usrgrpids, complex_pwd)
                results['zabbix'] = {"status": "success", "userid": z_result.get("userids", [""])[0]}
                audit_logger.info(f"IP: {requester_ip} | Target: Zabbix | Action: CREATE_USER | Status: SUCCESS | Alias: {alias} | RoleID: {roleid} | Groups: {usrgrpids}")
        except Exception as e:
            logger.error(f"Error provisioning Zabbix user {alias}: {str(e)}")
            results['zabbix'] = {"status": "error", "message": str(e)}
            audit_logger.error(f"IP: {requester_ip} | Target: Zabbix | Action: CREATE_USER | Status: ERROR | Alias: {alias} | Error: {str(e)}")
        finally:
            if auth_token:
                try:
                    zabbix_svc.logout(auth_token)
                except Exception as logout_err:
                    logger.error(f"Error logging out Zabbix: {str(logout_err)}")

    # Grafana Provisioning
    if 'grafana' in targets:
        grafana_svc = GrafanaService(GRAFANA_URL, GRAFANA_API_TOKEN)
        try:
            if grafana_svc.check_user_exists(email, alias):
                results['grafana'] = {"status": "error", "message": "User already exists"}
                audit_logger.warning(f"IP: {requester_ip} | Target: Grafana | Action: CREATE_USER | Status: FAILED (Already Exists) | Alias: {alias}")
            else:
                initial_pwd = generate_complex_password(12)
                full_name = f"{name} {surname}"
                g_result = grafana_svc.create_user(full_name, email, alias, initial_pwd)
                results['grafana'] = {"status": "success", "userId": g_result.get("id"), "initial_password": initial_pwd}
                audit_logger.info(f"IP: {requester_ip} | Target: Grafana | Action: CREATE_USER | Status: SUCCESS | Alias: {alias}")
        except Exception as e:
            logger.error(f"Error provisioning Grafana user {alias}: {str(e)}")
            results['grafana'] = {"status": "error", "message": str(e)}
            audit_logger.error(f"IP: {requester_ip} | Target: Grafana | Action: CREATE_USER | Status: ERROR | Alias: {alias} | Error: {str(e)}")

    # Determine overall status
    has_errors = any(res.get('status') == 'error' for res in results.values())
    status_code = 207 if has_errors else 200  # 207 Multi-Status
    if len(results) == 1 and has_errors:
        status_code = 500 if "Failed to communicate" in str(results) else 400

    return jsonify({
        "message": "Provisioning completed",
        **results
    }), status_code

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
