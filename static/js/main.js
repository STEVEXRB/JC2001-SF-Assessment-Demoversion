// main.js — Campus Market frontend logic
// Covers: view switching, item list and pagination, item detail, publishing,
// authentication, personal centre and direct messages.
// Depends on: api.js (API wrapper)

// ----------------------------- Global state -----------------------------
let currentUser = null;
let currentSellerId = null;
let currentSellerName = '';
let currentDetailItemId = null;
let currentDetailItem = null;
let currentPage = 1;
let totalPages = 1;
let currentCategory = '';
let currentProfileTab = 'items';
let favoriteIds = new Set();
let selectedImageFiles = [];
let pendingChat = null; // { id, name }

const CATEGORY_LABELS = {
    textbook: 'Textbook',
    digital: 'Electronics',
    daily_use: 'Daily use',
    sports_equipment: 'Sports gear',
    other: 'Other'
};

const CONDITION_LABELS = {
    new: 'Brand new',
    like_new: 'Like new',
    good: 'Good',
    fair: 'Fair'
};

const STATUS_LABELS = {
    ON_SALE: 'On sale',
    RESERVED: 'Reserved',
    SOLD: 'Sold',
    OFF_SHELF: 'Removed'
};

const MAX_IMAGES = 3;
const MAX_IMAGE_SIZE = 5 * 1024 * 1024;

// ----------------------------- Small helpers -----------------------------
const $ = id => document.getElementById(id);

function escapeHtml(value) {
    return String(value == null ? '' : value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function initial(name, fallback = 'U') {
    const text = String(name || '').trim();
    return text ? text.slice(0, 1).toUpperCase() : fallback;
}

function categoryLabel(key) { return CATEGORY_LABELS[key] || key || 'Uncategorised'; }
function conditionLabel(key) { return CONDITION_LABELS[key] || key || 'Not specified'; }
function statusLabel(status) { return STATUS_LABELS[status] || status; }

function money(value) {
    const num = Number(value);
    if (!isFinite(num)) return '0';
    return num % 1 === 0 ? String(num) : num.toFixed(2);
}

function parseTime(value) {
    if (!value) return null;
    const date = new Date(String(value).replace(' ', 'T') + 'Z');
    return isNaN(date.getTime()) ? null : date;
}

function timeAgo(value) {
    const date = parseTime(value);
    if (!date) return '';
    const diff = Math.max(0, (Date.now() - date.getTime()) / 1000);
    if (diff < 60) return 'just now';
    const plural = (n, unit) => `${n} ${unit}${n > 1 ? 's' : ''} ago`;
    if (diff < 3600) return plural(Math.floor(diff / 60), 'minute');
    if (diff < 86400) return plural(Math.floor(diff / 3600), 'hour');
    if (diff < 2592000) return plural(Math.floor(diff / 86400), 'day');
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// ----------------------------- Toasts and dialogs -----------------------------
function toast(message, type = 'info') {
    const root = $('toast-root');
    if (!root) return;
    const icons = { success: 'i-check', error: 'i-alert', info: 'i-bolt' };
    const node = document.createElement('div');
    node.className = 'toast is-' + type;
    node.innerHTML = `<svg class="icon"><use href="#${icons[type] || icons.info}"></use></svg><span>${escapeHtml(message)}</span>`;
    root.appendChild(node);
    const remove = () => {
        node.classList.add('is-leaving');
        setTimeout(() => node.remove(), 220);
    };
    setTimeout(remove, type === 'error' ? 4200 : 2800);
    node.addEventListener('click', remove);
}

function confirmDialog(title, description, okText = 'Confirm') {
    return new Promise(resolve => {
        $('confirm-title').textContent = title;
        $('confirm-desc').textContent = description;
        $('confirm-ok').textContent = okText;
        $('confirm-modal').classList.remove('hidden');

        const close = answer => {
            $('confirm-modal').classList.add('hidden');
            $('confirm-ok').removeEventListener('click', onOk);
            $('confirm-cancel').removeEventListener('click', onCancel);
            $('confirm-modal').removeEventListener('click', onBackdrop);
            resolve(answer);
        };
        const onOk = () => close(true);
        const onCancel = () => close(false);
        const onBackdrop = e => { if (e.target === $('confirm-modal')) close(false); };

        $('confirm-ok').addEventListener('click', onOk);
        $('confirm-cancel').addEventListener('click', onCancel);
        $('confirm-modal').addEventListener('click', onBackdrop);
    });
}

// ----------------------------- Bootstrap -----------------------------
document.addEventListener('DOMContentLoaded', initApp);

function initApp() {
    bindEvents();
    renderPublishPreview();
    showItemSkeleton();

    API.getMe()
        .then(res => { currentUser = res.data; updateUIForAuth(); })
        .catch(() => { currentUser = null; updateUIForAuth(); })
        .finally(() => { if (!applyRoute()) loadItems(); });
}

// Deep link to a single item via #item-<id>, so a listing can be shared as a link
function applyRoute() {
    const matched = /^#item-(\d+)$/.exec(location.hash);
    if (!matched) return false;
    openDetail(Number(matched[1]));
    return true;
}

function bindEvents() {
    // Header navigation
    $('home-btn').addEventListener('click', () => showView('home'));
    $('publish-btn').addEventListener('click', () => showView('publish'));
    $('profile-btn').addEventListener('click', () => { closeUserMenu(); showView('profile'); });
    $('menu-favorites-btn').addEventListener('click', () => { closeUserMenu(); showView('profile', 'favorites'); });
    $('menu-messages-btn').addEventListener('click', () => { closeUserMenu(); showView('profile', 'messages'); });
    $('login-btn').addEventListener('click', () => showView('auth'));
    $('logout-btn').addEventListener('click', () => { closeUserMenu(); logout(); });
    $('back-btn').addEventListener('click', () => showView('home'));

    // User dropdown
    $('user-menu-btn').addEventListener('click', e => {
        e.stopPropagation();
        $('user-menu-panel').classList.toggle('hidden');
    });
    document.addEventListener('click', e => {
        if (!$('user-menu').contains(e.target)) closeUserMenu();
    });
    document.addEventListener('keydown', e => {
        if (e.key !== 'Escape') return;
        closeUserMenu();
        $('message-modal').classList.add('hidden');
        if (!$('confirm-modal').classList.contains('hidden')) $('confirm-cancel').click();
    });

    // Keep the view in sync when the user navigates history or edits #item-<id>
    window.addEventListener('hashchange', () => {
        if (!applyRoute()) showView('home');
    });

    // Search
    $('search-form').addEventListener('submit', e => {
        e.preventDefault();
        currentPage = 1;
        loadItems();
    });

    // Category filter
    $('category-chips').addEventListener('click', e => {
        const chip = e.target.closest('.chip');
        if (!chip) return;
        currentCategory = chip.dataset.category || '';
        document.querySelectorAll('#category-chips .chip').forEach(c => {
            c.classList.toggle('is-active', c === chip);
        });
        currentPage = 1;
        loadItems();
    });

    // Sorting
    $('sort-select').addEventListener('change', () => {
        currentPage = 1;
        loadItems();
    });

    // Pagination
    $('prev-page').addEventListener('click', () => {
        if (currentPage > 1) { currentPage--; loadItems(); scrollToTop(); }
    });
    $('next-page').addEventListener('click', () => {
        if (currentPage < totalPages) { currentPage++; loadItems(); scrollToTop(); }
    });
    $('page-nums').addEventListener('click', e => {
        const btn = e.target.closest('.page-num');
        if (!btn || !btn.dataset.page) return;
        currentPage = Number(btn.dataset.page);
        loadItems();
        scrollToTop();
    });

    // Log in / sign up switch
    $('tab-login').addEventListener('click', () => switchAuthTab('login'));
    $('tab-register').addEventListener('click', () => switchAuthTab('register'));
    document.querySelectorAll('[data-switch]').forEach(link => {
        link.addEventListener('click', () => switchAuthTab(link.dataset.switch));
    });
    $('login-form').addEventListener('submit', handleLogin);
    $('register-form').addEventListener('submit', handleRegister);

    // Publish form
    $('publish-form').addEventListener('submit', handlePublish);
    $('publish-reset').addEventListener('click', resetPublishForm);
    $('item-images').addEventListener('change', handleImageSelect);
    bindPublishInputs();
    bindDropzone();
    bindChipGroup('item-category-chips', 'item-category');
    bindChipGroup('item-condition-chips', 'item-condition');

    // Personal centre
    $('tab-my-items').addEventListener('click', () => setProfileTab('items'));
    $('tab-my-favorites').addEventListener('click', () => setProfileTab('favorites'));
    $('tab-my-sold').addEventListener('click', () => setProfileTab('sold'));
    $('tab-messages').addEventListener('click', () => setProfileTab('messages'));

    // Direct messages
    $('close-message-modal').addEventListener('click', () => $('message-modal').classList.add('hidden'));
    $('message-modal').addEventListener('click', e => {
        if (e.target === $('message-modal')) $('message-modal').classList.add('hidden');
    });
    $('message-form').addEventListener('submit', e => {
        e.preventDefault();
        sendMessageFromModal();
    });
}

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ----------------------------- Auth state -----------------------------
function updateUIForAuth() {
    const loggedIn = !!currentUser;
    $('user-menu').classList.toggle('hidden', !loggedIn);
    $('login-btn').classList.toggle('hidden', loggedIn);
    $('publish-btn').classList.toggle('hidden', !loggedIn);

    if (loggedIn) {
        const name = currentUser.nickname || currentUser.username;
        $('nav-avatar').textContent = initial(name);
        $('nav-username').textContent = name;
        $('menu-nickname').textContent = name;
        $('menu-username').textContent = '@' + currentUser.username;
    } else {
        closeUserMenu();
        favoriteIds.clear();
    }
}

function closeUserMenu() {
    $('user-menu-panel').classList.add('hidden');
}

async function logout() {
    try {
        await API.logout();
    } catch (err) {
        /* Ignore network errors — clear the local state either way */
    }
    currentUser = null;
    favoriteIds.clear();
    updateUIForAuth();
    toast('You have been logged out');
    showView('home');
}

// ----------------------------- View switching -----------------------------
function showView(viewName, param) {
    if ((viewName === 'publish' || viewName === 'profile') && !currentUser) {
        toast('Please log in to continue', 'error');
        viewName = 'auth';
    }

    document.querySelectorAll('main > section').forEach(sec => sec.classList.add('hidden'));

    if (viewName === 'home') {
        $('home-view').classList.remove('hidden');
        loadItems();
    } else if (viewName === 'detail') {
        $('detail-view').classList.remove('hidden');
    } else if (viewName === 'publish') {
        $('publish-view').classList.remove('hidden');
        renderPublishPreview();
    } else if (viewName === 'auth') {
        $('auth-view').classList.remove('hidden');
    } else if (viewName === 'profile') {
        $('profile-view').classList.remove('hidden');
        renderProfileHead();
        setProfileTab(param || 'items');
    }
    window.scrollTo({ top: 0 });
}

// ----------------------------- Item list -----------------------------
function showItemSkeleton() {
    const grid = $('item-grid');
    grid.innerHTML = Array.from({ length: 8 }).map(() => `
        <div class="skeleton-card">
            <div class="skeleton thumb"></div>
            <div class="body">
                <div class="skeleton l1"></div>
                <div class="skeleton l2"></div>
                <div class="skeleton l3"></div>
            </div>
        </div>
    `).join('');
}

async function loadItems() {
    const keyword = $('search-input').value.trim();
    const sort = $('sort-select').value;
    showItemSkeleton();

    try {
        const res = await API.getItems({
            keyword,
            category: currentCategory,
            sort,
            page: currentPage,
            status: 'ON_SALE'
        });
        const data = res.data || {};
        totalPages = data.total_pages || 1;
        if (currentPage > totalPages) currentPage = totalPages;

        renderItems(data.items || []);
        updatePagination(data.total || 0);
        $('stat-on-sale').textContent = data.total || 0;
    } catch (err) {
        renderEmptyState('Could not load listings', err.message || 'Please try again in a moment');
        $('page-nums').innerHTML = '';
        $('page-info').textContent = '';
        $('result-count').textContent = '';
    }
}

function buildItemCard(item, options = {}) {
    const card = document.createElement('article');
    card.className = 'item-card';
    if (options.preview) card.classList.add('is-preview');

    const cover = item.cover_image
        ? `<img src="/uploads/${escapeHtml(item.cover_image)}" alt="${escapeHtml(item.title)}" loading="lazy">`
        : `<div class="no-img"><svg class="icon icon-lg"><use href="#i-image"></use></svg></div>`;

    const seller = item.seller_nickname || options.sellerFallback || 'Anonymous';

    card.innerHTML = `
        <div class="thumb">
            ${cover}
            <span class="badge badge-${escapeHtml(item.status)}">${escapeHtml(statusLabel(item.status))}</span>
        </div>
        <div class="card-body">
            <h3 class="card-title">${escapeHtml(item.title)}</h3>
            <div class="price-row">
                <span class="price"><i>¥</i>${escapeHtml(money(item.price))}</span>
                <span class="price-note">Pick up on campus</span>
            </div>
            <div class="card-meta">
                <span class="avatar avatar-xs">${escapeHtml(initial(seller))}</span>
                <span class="seller">${escapeHtml(seller)}</span>
                <span class="cat">${escapeHtml(categoryLabel(item.category))}</span>
            </div>
        </div>
    `;

    if (!options.preview) {
        card.addEventListener('click', () => openDetail(item.id));
    }
    return card;
}

function renderItems(items) {
    const grid = $('item-grid');
    grid.innerHTML = '';
    if (!items.length) {
        const keyword = $('search-input').value.trim();
        renderEmptyState(
            keyword ? 'No listings match your search' : 'No listings yet',
            keyword ? 'Try another keyword, or browse a different category' : 'Be the first to post something you no longer need'
        );
        return;
    }
    items.forEach(item => grid.appendChild(buildItemCard(item)));
}

function renderEmptyState(title, hint) {
    $('item-grid').innerHTML = `
        <div class="empty-state">
            <svg class="icon"><use href="#i-inbox"></use></svg>
            <strong>${escapeHtml(title)}</strong>
            <p>${escapeHtml(hint || '')}</p>
        </div>
    `;
}

function updatePagination(total) {
    const nums = $('page-nums');
    nums.innerHTML = '';
    $('result-count').textContent = total ? `${total} listing${total > 1 ? 's' : ''}` : '';
    $('page-info').textContent = totalPages > 1 ? `Page ${currentPage} of ${totalPages}` : '';
    $('prev-page').disabled = currentPage <= 1;
    $('next-page').disabled = currentPage >= totalPages;

    if (totalPages <= 1) return;

    const pages = [];
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || Math.abs(i - currentPage) <= 1) {
            pages.push(i);
        } else if (pages[pages.length - 1] !== '...') {
            pages.push('...');
        }
    }

    pages.forEach(page => {
        if (page === '...') {
            const span = document.createElement('span');
            span.className = 'page-num';
            span.textContent = '…';
            nums.appendChild(span);
            return;
        }
        const btn = document.createElement('button');
        btn.className = 'page-num' + (page === currentPage ? ' is-active' : '');
        btn.textContent = page;
        btn.dataset.page = page;
        nums.appendChild(btn);
    });
}

// ----------------------------- Item detail -----------------------------
async function openDetail(itemId) {
    showView('detail');
    $('detail-content').innerHTML = '<div class="loading-dots"><span></span><span></span><span></span></div>';

    try {
        const res = await API.getItemDetail(itemId);
        const item = res.data;
        currentDetailItem = item;
        currentDetailItemId = item.id;
        currentSellerId = item.seller_id;
        currentSellerName = item.seller_nickname || 'this seller';

        if (currentUser) {
            try {
                const fav = await API.getFavorites();
                favoriteIds = new Set((fav.data || []).map(row => row.id));
            } catch (err) {
                /* Failing to read the favorite state should not block the page */
            }
        }

        renderDetail(item);
    } catch (err) {
        $('detail-content').innerHTML = `
            <div class="empty-state">
                <svg class="icon"><use href="#i-alert"></use></svg>
                <strong>This listing could not be opened</strong>
                <p>${escapeHtml(err.message || '')}</p>
            </div>`;
    }
}

function renderDetail(item) {
    const images = item.images || [];
    const isOwner = currentUser && currentUser.id === item.seller_id;
    const isFavorited = favoriteIds.has(item.id);
    const seller = item.seller_nickname || 'Anonymous';

    const gallery = images.length
        ? `<div class="gallery-main"><img id="gallery-main-img" src="/uploads/${escapeHtml(images[0])}" alt="${escapeHtml(item.title)}"></div>
           ${images.length > 1 ? `<div class="gallery-thumbs" id="gallery-thumbs">
                ${images.map((img, i) => `
                    <button type="button" data-src="/uploads/${escapeHtml(img)}" class="${i === 0 ? 'is-active' : ''}">
                        <img src="/uploads/${escapeHtml(img)}" alt="Photo ${i + 1}">
                    </button>`).join('')}
           </div>` : ''}`
        : `<div class="gallery-main"><div class="no-img">
                <svg class="icon icon-lg"><use href="#i-image"></use></svg>
                <span>The seller has not uploaded any photos</span>
           </div></div>`;

    $('detail-content').innerHTML = `
        <div class="detail-layout">
            <div class="detail-main">
                <div class="gallery">${gallery}</div>

                <section class="card detail-block">
                    <h3>Description</h3>
                    <p class="detail-desc">${escapeHtml(item.description || 'The seller did not add a description.')}</p>
                </section>

                <section class="card detail-block">
                    <h3>Comments <span class="count">${(item.comments || []).length}</span></h3>
                    <div id="comment-list" class="comment-list">
                        ${renderCommentList(item.comments || [])}
                    </div>
                    ${renderCommentEditor()}
                </section>
            </div>

            <aside class="detail-side">
                <section class="card buy-card">
                    <div class="buy-top">
                        <span class="badge badge-${escapeHtml(item.status)}">${escapeHtml(statusLabel(item.status))}</span>
                        <h1>${escapeHtml(item.title)}</h1>
                    </div>

                    <div class="price-hero">
                        <i>¥</i><strong>${escapeHtml(money(item.price))}</strong>
                        <span class="price-note">Hand over in person</span>
                    </div>

                    <ul class="meta-list">
                        <li><svg class="icon icon-sm"><use href="#i-tag"></use></svg><span class="k">Category</span><span class="v">${escapeHtml(categoryLabel(item.category))}</span></li>
                        <li><svg class="icon icon-sm"><use href="#i-shield"></use></svg><span class="k">Condition</span><span class="v">${escapeHtml(conditionLabel(item.condition))}</span></li>
                        <li><svg class="icon icon-sm"><use href="#i-clock"></use></svg><span class="k">Posted</span><span class="v">${escapeHtml(timeAgo(item.created_at) || 'just now')}</span></li>
                        <li><svg class="icon icon-sm"><use href="#i-pin"></use></svg><span class="k">Handover</span><span class="v">On campus</span></li>
                    </ul>

                    <div class="buy-actions" id="detail-actions">${renderDetailActions(item, isOwner, isFavorited)}</div>

                    <div class="seller-card">
                        <span class="avatar">${escapeHtml(initial(seller))}</span>
                        <div class="seller-info">
                            <strong>${escapeHtml(seller)}${isOwner ? ' (you)' : ''}</strong>
                            <span>${isOwner ? 'This is your listing' : escapeHtml(item.seller_email || 'Contact details not shared')}</span>
                        </div>
                    </div>
                </section>

                <section class="tips-card safety-card">
                    <h3><svg class="icon icon-sm"><use href="#i-shield"></use></svg>Safety tips</h3>
                    <ul>
                        <li>Meet in a public spot on campus and inspect the item before paying.</li>
                        <li>The platform has no online payment — never transfer money in advance.</li>
                        <li>After the deal, ask the seller to mark the listing as sold.</li>
                    </ul>
                </section>
            </aside>
        </div>
    `;

    bindDetailEvents(item, isOwner);
}

function renderCommentList(comments) {
    if (!comments.length) {
        return '<p class="field-hint">No comments yet — be the first to ask something.</p>';
    }
    return comments.map(c => {
        const name = c.user_nickname || 'Anonymous';
        return `
            <div class="comment">
                <span class="avatar avatar-sm">${escapeHtml(initial(name))}</span>
                <div class="comment-body">
                    <div class="comment-head">
                        <strong>${escapeHtml(name)}</strong>
                        <time>${escapeHtml(timeAgo(c.created_at))}</time>
                    </div>
                    <p>${escapeHtml(c.content)}</p>
                </div>
            </div>`;
    }).join('');
}

function renderCommentEditor() {
    if (!currentUser) {
        return `<div class="comment-editor"><p class="login-hint">Log in to leave a comment for the seller</p></div>`;
    }
    return `
        <div class="comment-editor">
            <span class="avatar avatar-sm">${escapeHtml(initial(currentUser.nickname || currentUser.username))}</span>
            <textarea id="comment-input" rows="2" maxlength="200" placeholder="Anything you want to ask? e.g. Still available? Is the price negotiable?"></textarea>
            <button id="add-comment-btn" class="btn btn-primary">Post comment</button>
        </div>`;
}

function renderDetailActions(item, isOwner, isFavorited) {
    if (!currentUser) {
        return `<button class="btn btn-primary btn-lg btn-block" id="go-login-btn">Log in to contact the seller</button>`;
    }

    if (isOwner) {
        if (item.status === 'ON_SALE') {
            return `<button class="btn btn-danger-ghost btn-block" id="off-shelf-btn">Take listing offline</button>`;
        }
        if (item.status === 'RESERVED') {
            return `
                <button class="btn btn-primary btn-lg btn-block" id="sell-btn">Mark as sold</button>
                <button class="btn btn-ghost btn-block" id="cancel-reserve-btn">Cancel reservation and relist</button>`;
        }
        if (item.status === 'OFF_SHELF') {
            return `<button class="btn btn-primary btn-lg btn-block" id="relist-btn">Relist item</button>`;
        }
        return `<p class="login-hint">This item has been sold. Thanks for using Campus Market.</p>`;
    }

    const reserved = item.status === 'RESERVED';
    return `
        ${item.status === 'ON_SALE'
            ? `<button class="btn btn-primary btn-lg btn-block" id="reserve-btn">I want it — reserve</button>`
            : `<button class="btn btn-ghost btn-lg btn-block" disabled>${escapeHtml(statusLabel(item.status))} — not available to reserve</button>`}
        <div class="row">
            <button class="btn ${isFavorited ? 'btn-soft' : 'btn-ghost'}" id="favorite-btn">
                <svg class="icon icon-sm"><use href="#i-heart"></use></svg>${isFavorited ? 'Saved' : 'Save'}
            </button>
            <button class="btn btn-outline" id="contact-seller-btn">
                <svg class="icon icon-sm"><use href="#i-chat"></use></svg>Message seller
            </button>
        </div>
        ${reserved ? '<p class="login-hint">This item is already reserved — leave a comment to ask whether it is still available.</p>' : ''}
    `;
}

function bindDetailEvents(item, isOwner) {
    const thumbs = $('gallery-thumbs');
    if (thumbs) {
        thumbs.addEventListener('click', e => {
            const btn = e.target.closest('button');
            if (!btn) return;
            $('gallery-main-img').src = btn.dataset.src;
            thumbs.querySelectorAll('button').forEach(b => b.classList.toggle('is-active', b === btn));
        });
    }

    $('go-login-btn')?.addEventListener('click', () => showView('auth'));
    $('favorite-btn')?.addEventListener('click', toggleFavorite);
    $('contact-seller-btn')?.addEventListener('click', () => openConversation(item.seller_id, currentSellerName));
    $('reserve-btn')?.addEventListener('click', () =>
        changeStatus('reserve', 'Reserve this item', 'The seller will be notified. Do you want to reserve this item?', 'Reserve'));
    $('sell-btn')?.addEventListener('click', () =>
        changeStatus('sell', 'Mark as sold', 'Confirm that this deal is complete? The listing will be marked as sold.', 'Mark as sold'));
    $('cancel-reserve-btn')?.addEventListener('click', () =>
        changeStatus('cancel_reserve', 'Cancel reservation', 'The item will go back on sale and other students can reserve it again.', 'Cancel reservation'));
    $('off-shelf-btn')?.addEventListener('click', () =>
        changeStatus('off_shelf', 'Take listing offline', 'The listing will disappear from the list. You can relist it at any time.', 'Take offline'));
    $('relist-btn')?.addEventListener('click', () =>
        changeStatus('relist', 'Relist item', 'The listing will show up on the home page again.', 'Relist'));
    $('add-comment-btn')?.addEventListener('click', addComment);
}

async function toggleFavorite() {
    const itemId = currentDetailItemId;
    const isFavorited = favoriteIds.has(itemId);
    const btn = $('favorite-btn');
    if (btn) btn.disabled = true;

    try {
        if (isFavorited) {
            await API.removeFavorite(itemId);
            favoriteIds.delete(itemId);
            toast('Removed from your saved items');
        } else {
            await API.addFavorite(itemId);
            favoriteIds.add(itemId);
            toast('Saved — find it under your favorites', 'success');
        }
        if (btn) syncFavoriteButton(btn);
    } catch (err) {
        toast(err.message || 'That did not work, please try again', 'error');
    } finally {
        if (btn) btn.disabled = false;
    }
}

function syncFavoriteButton(btn) {
    const isFavorited = favoriteIds.has(currentDetailItemId);
    btn.className = 'btn ' + (isFavorited ? 'btn-soft' : 'btn-ghost');
    btn.innerHTML = `<svg class="icon icon-sm"><use href="#i-heart"></use></svg>${isFavorited ? 'Saved' : 'Save'}`;
}

async function changeStatus(action, title, desc, okText) {
    const ok = await confirmDialog(title, desc, okText);
    if (!ok) return;
    try {
        await API.changeItemStatus(currentDetailItemId, action);
        toast('Done', 'success');
        openDetail(currentDetailItemId);
    } catch (err) {
        toast(err.message || 'That did not work, please try again', 'error');
    }
}

async function addComment() {
    const input = $('comment-input');
    const content = input.value.trim();
    if (!content) {
        toast('Comment cannot be empty', 'error');
        input.focus();
        return;
    }
    const btn = $('add-comment-btn');
    btn.disabled = true;
    try {
        await API.addComment(currentDetailItemId, content);
        openDetail(currentDetailItemId);
        toast('Comment posted', 'success');
    } catch (err) {
        toast(err.message || 'Could not post the comment', 'error');
    } finally {
        btn.disabled = false;
    }
}

// ----------------------------- Publish -----------------------------
function bindChipGroup(groupId, selectId) {
    const group = $(groupId);
    const select = $(selectId);
    group.addEventListener('click', e => {
        const chip = e.target.closest('.chip');
        if (!chip) return;
        group.querySelectorAll('.chip').forEach(c => c.classList.toggle('is-active', c === chip));
        select.value = chip.dataset.value;
        renderPublishPreview();
    });
}

function bindPublishInputs() {
    ['item-title', 'item-desc', 'item-price'].forEach(id => {
        $(id).addEventListener('input', () => {
            if (id === 'item-desc') $('desc-counter').textContent = $('item-desc').value.length;
            renderPublishPreview();
        });
    });
}

function bindDropzone() {
    const zone = $('dropzone');
    ['dragenter', 'dragover'].forEach(evt =>
        zone.addEventListener(evt, e => { e.preventDefault(); zone.classList.add('is-over'); }));
    ['dragleave', 'drop'].forEach(evt =>
        zone.addEventListener(evt, e => { e.preventDefault(); zone.classList.remove('is-over'); }));
    zone.addEventListener('drop', e => addImageFiles(Array.from(e.dataTransfer.files || [])));
}

function handleImageSelect(e) {
    addImageFiles(Array.from(e.target.files || []));
    e.target.value = '';
}

function addImageFiles(files) {
    const accepted = [];
    for (const file of files) {
        if (selectedImageFiles.length + accepted.length >= MAX_IMAGES) {
            toast(`You can upload at most ${MAX_IMAGES} photos`, 'error');
            break;
        }
        if (!/^image\/(png|jpe?g|gif|webp)$/i.test(file.type)) {
            toast(`"${file.name}" is not a supported image type`, 'error');
            continue;
        }
        if (file.size > MAX_IMAGE_SIZE) {
            toast(`"${file.name}" is larger than 5 MB`, 'error');
            continue;
        }
        accepted.push(file);
    }
    selectedImageFiles = selectedImageFiles.concat(accepted);
    renderImagePreview();
}

function renderImagePreview() {
    const preview = $('image-preview');
    preview.innerHTML = '';
    selectedImageFiles.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'preview-item';
        item.innerHTML = `
            <img src="${URL.createObjectURL(file)}" alt="${escapeHtml(file.name)}">
            <button type="button" title="Remove" data-index="${index}">
                <svg class="icon-sm"><use href="#i-close"></use></svg>
            </button>`;
        preview.appendChild(item);
    });
    preview.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            selectedImageFiles.splice(Number(btn.dataset.index), 1);
            renderImagePreview();
        });
    });
    renderPublishPreview();
}

function renderPublishPreview() {
    const card = $('publish-preview');
    if (!card) return;
    const title = $('item-title').value.trim();
    const price = $('item-price').value;
    const category = $('item-category').value;
    const file = selectedImageFiles[0];

    const cover = file
        ? `<img src="${URL.createObjectURL(file)}" alt="">`
        : `<div class="no-img"><svg class="icon icon-lg"><use href="#i-image"></use></svg></div>`;

    card.innerHTML = `
        <div class="thumb">
            ${cover}
            <span class="badge badge-on_sale">On sale</span>
        </div>
        <div class="card-body">
            <h3 class="card-title">${escapeHtml(title || 'Your title will appear here')}</h3>
            <div class="price-row">
                <span class="price"><i>¥</i>${escapeHtml(price ? money(price) : '0')}</span>
                <span class="price-note">Pick up on campus</span>
            </div>
            <div class="card-meta">
                <span class="avatar avatar-xs">${escapeHtml(initial(currentUser ? (currentUser.nickname || currentUser.username) : 'You'))}</span>
                <span class="seller">${escapeHtml(currentUser ? (currentUser.nickname || currentUser.username) : 'You')}</span>
                <span class="cat">${escapeHtml(categoryLabel(category))}</span>
            </div>
        </div>
    `;
}

function resetPublishForm() {
    $('publish-form').reset();
    selectedImageFiles = [];
    renderImagePreview();
    $('desc-counter').textContent = '0';
    $('upload-status').textContent = '';
    $('upload-status').className = 'upload-status';
    document.querySelectorAll('#item-category-chips .chip').forEach((c, i) => c.classList.toggle('is-active', i === 0));
    $('item-category').value = 'textbook';
    document.querySelectorAll('#item-condition-chips .chip').forEach((c, i) => c.classList.toggle('is-active', i === 1));
    $('item-condition').value = 'like_new';
    renderPublishPreview();
}

async function handlePublish(e) {
    e.preventDefault();
    const title = $('item-title').value.trim();
    const description = $('item-desc').value.trim();
    const price = $('item-price').value;
    const category = $('item-category').value;
    const condition = $('item-condition').value;
    const status = $('upload-status');
    const submit = $('publish-submit');

    if (!title) { toast('Please enter a title', 'error'); $('item-title').focus(); return; }
    if (!price || Number(price) < 0) { toast('Please enter a valid price', 'error'); $('item-price').focus(); return; }
    if (!selectedImageFiles.length) { toast('Please add at least one photo', 'error'); return; }

    submit.disabled = true;
    status.className = 'upload-status';
    status.textContent = 'Uploading photos…';

    try {
        const formData = new FormData();
        selectedImageFiles.forEach(file => formData.append('files', file));
        const uploadRes = await API.uploadImages(formData);
        const imageNames = uploadRes.data || [];

        status.textContent = 'Publishing your listing…';
        await API.createItem({
            title,
            description,
            price: parseFloat(price),
            category,
            condition,
            images: imageNames
        });

        status.className = 'upload-status is-ok';
        status.textContent = 'Published — taking you back to the home page…';
        toast('Your listing is live', 'success');
        resetPublishForm();
        currentPage = 1;
        showView('home');
    } catch (err) {
        status.className = 'upload-status is-error';
        status.textContent = err.message || 'Publishing failed, please try again';
        toast(err.message || 'Publishing failed', 'error');
    } finally {
        submit.disabled = false;
    }
}

// ----------------------------- Log in / sign up -----------------------------
function switchAuthTab(tab) {
    const isLogin = tab === 'login';
    $('login-form').classList.toggle('hidden', !isLogin);
    $('register-form').classList.toggle('hidden', isLogin);
    $('tab-login').classList.toggle('is-active', isLogin);
    $('tab-register').classList.toggle('is-active', !isLogin);
    $('tab-login').setAttribute('aria-selected', String(isLogin));
    $('tab-register').setAttribute('aria-selected', String(!isLogin));
}

async function handleLogin(e) {
    e.preventDefault();
    const form = $('login-form');
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    try {
        const res = await API.login($('login-username').value.trim(), $('login-password').value);
        currentUser = res.data;
        // The login endpoint only returns id / username, so load the full profile
        try {
            const me = await API.getMe();
            currentUser = me.data;
        } catch (err) {
            /* Fall back to the basic info if the profile request fails */
        }
        updateUIForAuth();
        form.reset();
        toast(`Welcome back, ${currentUser.nickname || currentUser.username}`, 'success');
        showView('home');
    } catch (err) {
        toast(err.message || 'Could not log you in', 'error');
    } finally {
        btn.disabled = false;
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const form = $('register-form');
    const btn = form.querySelector('button[type="submit"]');
    const username = $('reg-username').value.trim();
    const password = $('reg-password').value;

    if (password.length < 6) {
        toast('Password must be at least 6 characters', 'error');
        $('reg-password').focus();
        return;
    }

    btn.disabled = true;
    try {
        await API.register({
            username,
            password,
            nickname: $('reg-nickname').value.trim(),
            email: $('reg-email').value.trim(),
            student_id: $('reg-student-id').value.trim()
        });
        toast('Account created — please log in', 'success');
        form.reset();
        switchAuthTab('login');
        $('login-username').value = username;
        $('login-password').focus();
    } catch (err) {
        toast(err.message || 'Could not create the account', 'error');
    } finally {
        btn.disabled = false;
    }
}

// ----------------------------- Personal centre -----------------------------
function renderProfileHead() {
    if (!currentUser) return;
    const name = currentUser.nickname || currentUser.username;
    $('profile-avatar').textContent = initial(name);
    $('profile-nickname').textContent = name;
    $('profile-username').textContent = '@' + currentUser.username;
    $('profile-student-id').textContent = currentUser.student_id || 'not set';
    loadProfileStats();
}

async function loadProfileStats() {
    const set = (id, value) => { $(id).textContent = value == null ? '–' : value; };
    try {
        const [items, favorites, sold] = await Promise.all([
            API.getMyItems(),
            API.getFavorites(),
            API.getSoldItems()
        ]);
        set('stat-my-items', (items.data || []).length);
        set('stat-my-favorites', (favorites.data || []).length);
        set('stat-my-sold', (sold.data || []).length);
    } catch (err) {
        set('stat-my-items', 0);
        set('stat-my-favorites', 0);
        set('stat-my-sold', 0);
    }
}

function setProfileTab(tab) {
    currentProfileTab = tab;
    const tabIds = {
        items: 'tab-my-items',
        favorites: 'tab-my-favorites',
        sold: 'tab-my-sold',
        messages: 'tab-messages'
    };
    document.querySelectorAll('#profile-view .tabs-underline .tab').forEach(el => {
        el.classList.toggle('is-active', el.id === tabIds[tab]);
    });
    loadProfileData(tab);
}

async function loadProfileData(tab) {
    const container = $('profile-content');
    container.innerHTML = '<div class="loading-dots"><span></span><span></span><span></span></div>';
    try {
        if (tab === 'messages') {
            const res = await API.getMessages();
            renderMessages(res.data || []);
        } else {
            const res = tab === 'favorites' ? await API.getFavorites()
                : tab === 'sold' ? await API.getSoldItems()
                : await API.getMyItems();
            renderProfileItems(res.data || [], tab);
        }
    } catch (err) {
        container.innerHTML = `
            <div class="empty-state">
                <svg class="icon"><use href="#i-alert"></use></svg>
                <strong>Could not load this section</strong>
                <p>${escapeHtml(err.message || '')}</p>
            </div>`;
    }
}

function renderProfileItems(items, tab) {
    const container = $('profile-content');
    if (!items.length) {
        const texts = {
            items: ['You have not posted anything yet', 'List something you no longer need and let a classmate find it'],
            favorites: ['Your saved list is empty', 'Tap "Save" on a listing and it will show up here'],
            sold: ['No completed deals yet', 'Listings appear here once you mark them as sold']
        };
        const [title, hint] = texts[tab] || ['Nothing here yet', ''];
        container.innerHTML = `
            <div class="empty-state">
                <svg class="icon"><use href="#i-inbox"></use></svg>
                <strong>${escapeHtml(title)}</strong>
                <p>${escapeHtml(hint)}</p>
            </div>`;
        return;
    }

    const grid = document.createElement('div');
    grid.className = 'item-grid';
    // /api/user/items and /api/user/sold do not return the seller nickname, so fall back to "You"
    const sellerFallback = (tab === 'items' || tab === 'sold') ? 'You' : 'Anonymous';
    items.forEach(item => grid.appendChild(buildItemCard(item, { sellerFallback })));
    container.innerHTML = '';
    container.appendChild(grid);
}

function renderMessages(messages) {
    const container = $('profile-content');
    if (!messages.length) {
        container.innerHTML = `
            <div class="empty-state">
                <svg class="icon"><use href="#i-chat"></use></svg>
                <strong>No messages yet</strong>
                <p>Tap "Message seller" on a listing to start a conversation</p>
            </div>`;
        return;
    }

    const list = document.createElement('div');
    list.className = 'conv-list';
    messages.forEach(msg => {
        const isMine = msg.sender_id === currentUser.id;
        const otherId = isMine ? msg.receiver_id : msg.sender_id;
        const otherName = msg.other_nickname || 'User ' + otherId;

        const row = document.createElement('button');
        row.type = 'button';
        row.className = 'conv';
        row.innerHTML = `
            <span class="avatar">${escapeHtml(initial(otherName))}</span>
            <div class="conv-main">
                <div class="conv-head">
                    <strong>${escapeHtml(otherName)}</strong>
                    <time>${escapeHtml(timeAgo(msg.created_at))}</time>
                </div>
                <p>${isMine ? 'You: ' : ''}${escapeHtml(msg.content)}</p>
            </div>
            <span class="conv-cta">Open</span>
        `;
        row.addEventListener('click', () => openConversation(otherId, otherName));
        list.appendChild(row);
    });

    container.innerHTML = '';
    container.appendChild(list);
}

// ----------------------------- Direct messages -----------------------------
async function openConversation(otherUserId, otherName) {
    pendingChat = { id: otherUserId, name: otherName || 'Student' };
    $('message-receiver').textContent = pendingChat.name;
    $('chat-avatar').textContent = initial(pendingChat.name);
    $('message-modal').classList.remove('hidden');
    $('message-list').innerHTML = '<div class="loading-dots"><span></span><span></span><span></span></div>';

    try {
        const res = await API.getConversation(otherUserId);
        renderConversation(res.data || []);
    } catch (err) {
        $('message-list').innerHTML = `<p class="login-hint">${escapeHtml(err.message || 'Could not load this conversation')}</p>`;
    }
}

function renderConversation(messages) {
    const list = $('message-list');
    if (!messages.length) {
        list.innerHTML = '<p class="login-hint">No messages yet — say hello.</p>';
        return;
    }
    list.innerHTML = messages.map(m => {
        const own = m.sender_id === currentUser.id;
        return `<div class="bubble ${own ? 'own' : ''}">
            ${escapeHtml(m.content)}
            <time>${escapeHtml(timeAgo(m.created_at))}</time>
        </div>`;
    }).join('');
    list.scrollTop = list.scrollHeight;
}

async function sendMessageFromModal() {
    if (!pendingChat) return;
    const input = $('message-text');
    const content = input.value.trim();
    if (!content) return;

    const btn = $('send-message-btn');
    btn.disabled = true;
    try {
        await API.sendMessage(pendingChat.id, content, currentDetailItemId);
        input.value = '';
        const res = await API.getConversation(pendingChat.id);
        renderConversation(res.data || []);
    } catch (err) {
        toast(err.message || 'Message could not be sent', 'error');
    } finally {
        btn.disabled = false;
        input.focus();
    }
}
