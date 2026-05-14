class AppStore {
    constructor() {
        this.state = {
            isLoading: false,
            notification: null // { type: 'success' | 'error', message: string }
        };
        this.listeners = [];
    }

    getState() {
        return this.state;
    }

    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.notifyListeners();
    }

    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    notifyListeners() {
        this.listeners.forEach(listener => listener(this.state));
    }

    setLoading(isLoading) {
        this.setState({ isLoading });
    }

    setNotification(type, message) {
        this.setState({ notification: { type, message } });
    }

    clearNotification() {
        this.setState({ notification: null });
    }
}

export const store = new AppStore();
