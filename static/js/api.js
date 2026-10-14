// api.js - wraps backend API requests
const API = {
    baseURL: '',

    async request(url, method = 'GET', body = null, isForm = false, options = {}) {
        const headers = { ...(options.headers || {}) };
        const fetchOptions = {
            method,
            credentials: 'include',
            headers,
            ...options
        };

        if (body !== null && body !== undefined) {
            if (isForm) {
                fetchOptions.body = body;
            } else {
                headers['Content-Type'] = headers['Content-Type'] || 'application/json; charset=utf-8';
                fetchOptions.body = JSON.stringify(body);
            }
        }

        const finalUrl = url.startsWith('http') ? url : `${this.baseURL}${url}`;

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), options.timeout || 10000);
        fetchOptions.signal = controller.signal;

        try {
            const response = await fetch(finalUrl, fetchOptions);

            const contentType = (response.headers.get('content-type') || '').toLowerCase();
            const rawText = await response.text();
            const data = rawText && contentType.includes('application/json')
                ? JSON.parse(rawText)
                : (rawText || null);

            if (!response.ok) {
                const msg =
                    (data && (data.msg || data.error || data.message || data.detail)) ||
                    rawText ||
                    'Request failed';

                throw new Error(msg || 'Request failed');
            }

            return data;
        } catch (error) {
            if (error && error.name === 'AbortError') {
                throw new Error('Request timed out');
            }
            throw error instanceof Error ? error : new Error('Request failed');
        } finally {
            clearTimeout(timeoutId);
        }
    },

    // User related
    register(userData) { return this.request('/api/register', 'POST', userData); },
    login(username, password) { return this.request('/api/login', 'POST', { username, password }); },
    logout() { return this.request('/api/logout', 'POST'); },
    getMe() { return this.request('/api/user/me'); },

    // Product related
    getItems(params = {}) {
        const safeParams = Object.fromEntries(
            Object.entries(params).filter(([, value]) => value !== null && value !== undefined && value !== '')
        );
        const query = new URLSearchParams(safeParams).toString();
        return this.request(query ? `/api/items?${query}` : '/api/items');
    },
    getItemDetail(id) { return this.request(`/api/items/${id}`); },
    createItem(itemData) { return this.request('/api/items', 'POST', itemData); },
    updateItem(id, itemData) { return this.request(`/api/items/${id}`, 'PUT', itemData); },
    deleteItem(id) { return this.request(`/api/items/${id}`, 'DELETE'); },
    changeItemStatus(id, action) { return this.request(`/api/items/${id}/status`, 'POST', { action }); },

    // Image upload
    uploadImages(formData) { return this.request('/api/upload', 'POST', formData, true); },

    // Favorites
    addFavorite(itemId) { return this.request('/api/favorites', 'POST', { item_id: itemId }); },
    removeFavorite(itemId) { return this.request(`/api/favorites/${itemId}`, 'DELETE'); },
    getFavorites() { return this.request('/api/favorites'); },

    // Comments
    getComments(itemId) { return this.request(`/api/items/${itemId}/comments`); },
    addComment(itemId, content) { return this.request(`/api/items/${itemId}/comments`, 'POST', { content }); },

    // Private messages
    sendMessage(receiverId, content, itemId = null) {
        return this.request('/api/messages', 'POST', { receiver_id: receiverId, content, item_id: itemId });
    },
    getMessages() { return this.request('/api/messages'); },
    getConversation(userId) { return this.request(`/api/messages/${userId}`); },

    // Personal center
    getMyItems() { return this.request('/api/user/items'); },
    getSoldItems() { return this.request('/api/user/sold'); }
};
