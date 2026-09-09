// main.js - frontend page logic
let currentSellerId = null;
let currentUser = null;
let currentPage = 1;
let totalPages = 1;
let currentDetailItemId = null;
let selectedImageFiles = []; // temporarily store selected image files

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    // Check login status
    API.getMe().then(res => {
        currentUser = res.data;
        updateUIForAuth();
    }).catch(() => {
        currentUser = null;
        updateUIForAuth();
    });

    // Bind events
    bindEvents();
    // Load homepage items
    loadItems();
}

function bindEvents() {
    // Navigation buttons
    document.getElementById('home-btn').addEventListener('click', () => showView('home'));
    document.getElementById('publish-btn').addEventListener('click', () => showView('publish'));
    document.getElementById('profile-btn').addEventListener('click', () => showView('profile'));
    document.getElementById('login-btn').addEventListener('click', () => showView('auth'));
    document.getElementById('logout-btn').addEventListener('click', logout);
    document.getElementById('back-btn').addEventListener('click', () => showView('home'));

    // Search
    document.getElementById('search-btn').addEventListener('click', () => {
        currentPage = 1;
        loadItems();
    });
    document.getElementById('search-input').addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
            currentPage = 1;
            loadItems();
        }
    });

    // Category and sorting
    document.getElementById('category-filter').addEventListener('change', () => {
        currentPage = 1;
        loadItems();
    });
    document.getElementById('sort-select').addEventListener('change', () => {
        currentPage = 1;
        loadItems();
    });

    // Pagination
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadItems();
        }
    });
    document.getElementById('next-page').addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            loadItems();
        }
    });

    // Login/register switch
    document.getElementById('tab-login').addEventListener('click', () => {
        document.getElementById('login-form').classList.remove('hidden');
        document.getElementById('register-form').classList.add('hidden');
        document.getElementById('tab-login').classList.add('active');
        document.getElementById('tab-register').classList.remove('active');
    });
    document.getElementById('tab-register').addEventListener('click', () => {
        document.getElementById('register-form').classList.remove('hidden');
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('tab-register').classList.add('active');
        document.getElementById('tab-login').classList.remove('active');
    });

    // Login form
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);

    // Publish form
    document.getElementById('publish-form').addEventListener('submit', handlePublish);

    // Image selection preview
    document.getElementById('item-images').addEventListener('change', handleImageSelect);

    // Personal center tabs
    document.getElementById('tab-my-items').addEventListener('click', () => loadProfileData('items'));
    document.getElementById('tab-my-favorites').addEventListener('click', () => loadProfileData('favorites'));
    document.getElementById('tab-my-sold').addEventListener('click', () => loadProfileData('sold'));
    document.getElementById('tab-messages').addEventListener('click', () => loadProfileData('messages'));

    // Message modal close
    document.getElementById('close-message-modal').addEventListener('click', () => {
        document.getElementById('message-modal').classList.add('hidden');
    });
    document.getElementById('send-message-btn').addEventListener('click', sendMessageFromModal);
}

function updateUIForAuth() {
    const loggedIn = !!currentUser;
    document.querySelectorAll('.hidden-when-logout').forEach(el => {
        el.classList.toggle('hidden', !loggedIn);
    });
    document.getElementById('login-btn').classList.toggle('hidden', loggedIn);
    document.getElementById('logout-btn').classList.toggle('hidden', !loggedIn);
}

function showView(viewName) {
    document.querySelectorAll('main > section').forEach(sec => sec.classList.add('hidden'));
    if (viewName === 'home') {
        document.getElementById('home-view').classList.remove('hidden');
        loadItems();
    } else if (viewName === 'detail') {
        document.getElementById('detail-view').classList.remove('hidden');
    } else if (viewName === 'publish') {
        if (!currentUser) {
            alert('Please log in first');
            showView('auth');
            return;
        }
        document.getElementById('publish-view').classList.remove('hidden');
    } else if (viewName === 'auth') {
        document.getElementById('auth-view').classList.remove('hidden');
    } else if (viewName === 'profile') {
        if (!currentUser) {
            alert('Please log in first');
            showView('auth');
            return;
        }
        document.getElementById('profile-view').classList.remove('hidden');
        loadProfileData('items');
    }
}

// ---------- Product list ----------
async function loadItems() {
    const keyword = document.getElementById('search-input').value.trim();
    const category = document.getElementById('category-filter').value;
    const sort = document.getElementById('sort-select').value;
    try {
        const res = await API.getItems({
            keyword,
            category,
            sort,
            page: currentPage,
            status: 'ON_SALE' // Show only items currently on sale
        });
        totalPages = res.data.total_pages || 1;
        renderItems(res.data.items);
        document.getElementById('page-info').textContent = `Page ${currentPage} of ${totalPages}`;
    } catch (err) {
        alert(err.message);
    }
}

function renderItems(items) {
    const grid = document.getElementById('item-grid');
    grid.innerHTML = '';
    if (!items || items.length === 0) {
        grid.innerHTML = '<p>No items available</p>';
        return;
    }
    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'item-card';
        card.innerHTML = `
            <img src="${item.cover_image ? '/uploads/' + item.cover_image : '/static/images/default.png'}" alt="${item.title}">
            <div class="info">
                <div class="title">${item.title}</div>
                <div class="price">¥${item.price}</div>
                <span class="status status-${item.status}">${statusText(item.status)}</span>
                <div class="seller">Seller: ${item.seller_nickname || 'Unknown'}</div>
            </div>
        `;
        card.addEventListener('click', () => openDetail(item.id));
        grid.appendChild(card);
    });
}

function statusText(status) {
    const map = {
        'ON_SALE': 'On Sale',
        'RESERVED': 'Reserved',
        'SOLD': 'Sold',
        'OFF_SHELF': 'Removed'
    };
    return map[status] || status;
}

// ---------- Product details ----------
async function openDetail(itemId) {
    try {
        const res = await API.getItemDetail(itemId);
        const item = res.data;
        currentDetailItemId = itemId;
        currentSellerId = item.seller_id;
        const container = document.getElementById('detail-content');
        container.innerHTML = `
            <h2>${item.title}</h2>
            <div class="detail-images">
                ${item.images.map(img => `<img src="/uploads/${img}" alt="">`).join('') || '<p>No images</p>'}
            </div>
            <p><strong>Price:</strong> ¥${item.price}</p>
            <p><strong>Condition:</strong> ${item.condition || 'Not specified'}</p>
            <p><strong>Category:</strong> ${item.category}</p>
            <p><strong>Description:</strong> ${item.description || 'None'}</p>
            <p><strong>Seller:</strong> ${item.seller_nickname || 'Unknown'} (${item.seller_email || ''})</p>
            <p><strong>Status:</strong> ${statusText(item.status)}</p>
            <div class="actions">
                ${!currentUser ? '' : `
                    <button id="favorite-btn">Favorite</button>
                    <button id="contact-seller-btn">Message Seller</button>
                    ${item.status === 'ON_SALE' && currentUser.id !== item.seller_id ? '<button id="reserve-btn">I want it</button>' : ''}
                    ${currentUser.id === item.seller_id && item.status === 'RESERVED' ? '<button id="sell-btn">Confirm Sale</button>' : ''}
                    ${currentUser.id === item.seller_id && item.status === 'ON_SALE' ? '<button id="off-shelf-btn">Take Offline</button>' : ''}
                `}
            </div>
            <div class="comments">
                <h3>Comments</h3>
                <div id="comment-list">
                    ${item.comments.map(c => `<p><strong>${c.user_nickname}</strong>: ${c.content}</p>`).join('')}
                </div>
                ${currentUser ? `
                    <textarea id="comment-input" placeholder="Leave a comment..."></textarea>
                    <button id="add-comment-btn">Comment</button>
                ` : '<p>Please log in to leave a comment</p>'}
            </div>
        `;
        showView('detail');

        // Bind detail page button events
        if (currentUser) {
            document.getElementById('favorite-btn')?.addEventListener('click', toggleFavorite);
            document.getElementById('contact-seller-btn')?.addEventListener('click', openMessageModal);
            document.getElementById('reserve-btn')?.addEventListener('click', () => changeStatus('reserve'));
            document.getElementById('sell-btn')?.addEventListener('click', () => changeStatus('sell'));
            document.getElementById('off-shelf-btn')?.addEventListener('click', () => changeStatus('off_shelf'));
            document.getElementById('add-comment-btn')?.addEventListener('click', addComment);
        }
    } catch (err) {
        alert(err.message);
    }
}

async function toggleFavorite() {
    // Simplified: if already favorited, remove it; otherwise add it. In practice, the favorite status should be checked first.
    try {
        await API.addFavorite(currentDetailItemId);
        alert('Added to favorites successfully');
    } catch (err) {
        alert(err.message);
    }
}

async function changeStatus(action) {
    try {
        await API.changeItemStatus(currentDetailItemId, action);
        alert('Action successful');
        openDetail(currentDetailItemId); // Refresh detail
    } catch (err) {
        alert(err.message);
    }
}

async function addComment() {
    const content = document.getElementById('comment-input').value.trim();
    if (!content) return alert('Comment content cannot be empty');
    try {
        await API.addComment(currentDetailItemId, content);
        openDetail(currentDetailItemId);
    } catch (err) {
        alert(err.message);
    }
}

// ---------- Publish item ----------
async function handlePublish(e) {
    e.preventDefault();
    const title = document.getElementById('item-title').value.trim();
    const description = document.getElementById('item-desc').value.trim();
    const price = document.getElementById('item-price').value;
    const category = document.getElementById('item-category').value;
    const condition = document.getElementById('item-condition').value;

    let imageNames = [];
    if (selectedImageFiles.length > 0) {
        // Upload images first
        const formData = new FormData();
        selectedImageFiles.forEach(file => formData.append('files', file));
        try {
            const uploadRes = await API.uploadImages(formData);
            imageNames = uploadRes.data;
        } catch (err) {
            alert('Image upload failed: ' + err.message);
            return;
        }
    }

    try {
        await API.createItem({
            title,
            description,
            price: parseFloat(price),
            category,
            condition,
            images: imageNames
        });
        alert('Published successfully!');
        selectedImageFiles = [];
        document.getElementById('publish-form').reset();
        document.getElementById('image-preview').innerHTML = '';
        showView('home');
    } catch (err) {
        alert(err.message);
    }
}

function handleImageSelect(e) {
    selectedImageFiles = Array.from(e.target.files).slice(0, 3);
    const preview = document.getElementById('image-preview');
    preview.innerHTML = '';
    selectedImageFiles.forEach(file => {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.height = 100;
        preview.appendChild(img);
    });
}

// ---------- Login/register ----------
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    try {
        const res = await API.login(username, password);
        currentUser = res.data;
        updateUIForAuth();
        alert('Login successful');
        showView('home');
    } catch (err) {
        alert(err.message);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value;
    const nickname = document.getElementById('reg-nickname').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const student_id = document.getElementById('reg-student-id').value.trim();
    try {
        await API.register({ username, password, nickname, email, student_id });
        alert('Registration successful. Please log in.');
        // Switch to the login form
        document.getElementById('tab-login').click();
        document.getElementById('login-username').value = username;
    } catch (err) {
        alert(err.message);
    }
}

async function logout() {
    await API.logout();
    currentUser = null;
    updateUIForAuth();
    showView('home');
}

// ---------- Personal center ----------
async function loadProfileData(tab) {
    const container = document.getElementById('profile-content');
    container.innerHTML = '<p>Loading...</p>';
    try {
        if (tab === 'items') {
            const res = await API.getMyItems();
            renderProfileItems(res.data);
        } else if (tab === 'favorites') {
            const res = await API.getFavorites();
            renderProfileItems(res.data);
        } else if (tab === 'sold') {
            const res = await API.getSoldItems();
            renderProfileItems(res.data);
        } else if (tab === 'messages') {
            const res = await API.getMessages();
            renderMessages(res.data);
        }
    } catch (err) {
        container.innerHTML = `<p>Failed to load: ${err.message}</p>`;
    }
}

function renderProfileItems(items) {
    const container = document.getElementById('profile-content');
    if (!items || items.length === 0) {
        container.innerHTML = '<p>No data available</p>';
        return;
    }
    container.innerHTML = items.map(item => `
        <div class="item-card" onclick="openDetail(${item.id})">
            <img src="${item.cover_image ? '/uploads/' + item.cover_image : '/static/images/default.png'}">
            <div class="info">
                <div class="title">${item.title}</div>
                <div class="price">¥${item.price}</div>
                <span class="status status-${item.status}">${statusText(item.status)}</span>
            </div>
        </div>
    `).join('');
}

function renderMessages(messages) {
    const container = document.getElementById('profile-content');
    if (!messages || messages.length === 0) {
        container.innerHTML = '<p>No messages</p>';
        return;
    }
    container.innerHTML = messages.map(msg => {
        const otherName = msg.other_nickname || 'User ' + (msg.sender_id === currentUser.id ? msg.receiver_id : msg.sender_id);
        return `<div class="message-item" data-other-id="${msg.sender_id === currentUser.id ? msg.receiver_id : msg.sender_id}">
            <strong>${otherName}</strong>: ${msg.content}
            <button class="open-chat-btn">Open chat</button>
        </div>`;
    }).join('');
    document.querySelectorAll('.open-chat-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const otherId = e.target.closest('.message-item').dataset.otherId;
            openConversation(otherId);
        });
    });
}

// ---------- Private messages ----------
function openMessageModal() {
    if (!currentSellerId) {
        alert('Unable to get seller information');
        return;
    }
    openConversation(currentSellerId);
}

async function openConversation(otherUserId) {
    try {
        const res = await API.getConversation(otherUserId);
        const messages = res.data;
        document.getElementById('message-receiver').textContent = otherUserId;
        const list = document.getElementById('message-list');
        list.innerHTML = messages.map(m => `
            <div class="message-item ${m.sender_id === currentUser.id ? 'own' : ''}">
                <strong>${m.sender_id === currentUser.id ? 'Me' : 'Other'}</strong>: ${m.content}
            </div>
        `).join('');
        document.getElementById('message-modal').classList.remove('hidden');
        // Save recipient ID for sending
        document.getElementById('message-modal').dataset.receiverId = otherUserId;
    } catch (err) {
        alert(err.message);
    }
}

async function sendMessageFromModal() {
    const receiverId = document.getElementById('message-modal').dataset.receiverId;
    const content = document.getElementById('message-text').value.trim();
    if (!receiverId || !content) return;
    try {
        await API.sendMessage(receiverId, content, currentDetailItemId);
        document.getElementById('message-text').value = '';
        openConversation(receiverId); // Refresh conversation
    } catch (err) {
        alert(err.message);
    }
}