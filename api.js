// api.js - wraps backend API requests
const API = {
    // Generic request method
    async request(url, method = 'GET', body = null, isForm = false) {
        const options = {
            method,
            headers: {}
        };
        if (body) {
            if (isForm) {
                options.body = body;
            } else {
                options.headers['Content-Type'] = 'application/json';
                options.body = JSON.stringify(body);
            }
        }
        const response = await fetch(url, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.msg || 'Request failed');
        }
        return data;
    },

    // User related
    register(userData) { return this.request('/api/register', 'POST', userData); },
    login(username, password) { return this.request('/api/login', 'POST', { username, password }); },
    logout() { return this.request('/api/logout', 'POST'); },
    getMe() { return this.request('/api/user/me'); },

    // Product related
    getItems(params) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/items?${query}`);
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