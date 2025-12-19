<script lang="ts">
	import logoImg from '$lib/assets/logo.png'
	import logoWhiteImg from '$lib/assets/logo_white.png'
	import Checkbox from '$lib/components/Checkbox.svelte'
	import { auth, isAdmin, isAuthenticated } from '$lib/stores/auth'
	import { cubicOut } from 'svelte/easing'
	import { fade, fly } from 'svelte/transition'

	let isMenuOpen = $state(false)
	let isSearchOpen = $state(false)
	let isAdminMenuOpen = $state(false)
	let searchQuery = $state('')
	let exactSearch = $state(false)

	function toggleMenu() {
		isMenuOpen = !isMenuOpen
		if (isMenuOpen) isSearchOpen = false
		if (!isMenuOpen) isAdminMenuOpen = false
	}

	function toggleSearch() {
		isSearchOpen = !isSearchOpen
		if (isSearchOpen) isMenuOpen = false
	}

	function toggleAdminMenu() {
		isAdminMenuOpen = !isAdminMenuOpen
	}

	function handleSearch() {
		if (searchQuery.trim()) {
			const params = new URLSearchParams()
			params.set('query', searchQuery.trim())
			if (exactSearch) params.set('exact', 'true')
			window.location.href = `/search?${params.toString()}`
		}
	}

	function handleSearchKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			handleSearch()
		}
	}

	function handleLogout() {
		auth.logout()
		window.location.href = '/'
	}
</script>

<!-- Шапка (Header) -->
<header class="header">
	<div class="header-left">
		<button class="menu-btn" onclick={toggleMenu} aria-label="Меню">
			<svg
				width="32"
				height="32"
				viewBox="0 0 32 32"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M4 8H28M4 16H28M4 24H28"
					stroke="#333333"
					stroke-width="2"
					stroke-linecap="round"
				/>
			</svg>
		</button>

		<a href="/" class="logo-container">
			<img src={logoImg} alt="Логотип" class="logo-img" />
		</a>
	</div>

	<div class="header-right">
		<button class="search-trigger" onclick={toggleSearch}>
			<div class="search-icon-wrapper">
				{#if isSearchOpen}
					<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
						<path
							d="M18 6L6 18M6 6L18 18"
							stroke="#333333"
							stroke-width="2"
							stroke-linecap="round"
						/>
					</svg>
				{:else}
					<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
						<circle cx="11" cy="11" r="7" stroke="#333333" stroke-width="2" />
						<path
							d="M16 16L21 21"
							stroke="#333333"
							stroke-width="2"
							stroke-linecap="round"
						/>
					</svg>
				{/if}
			</div>
			<span class="search-label">{isSearchOpen ? 'Закрыть' : 'Поиск'}</span>
		</button>

		{#if $isAuthenticated}
			<button class="btn-secondary" onclick={handleLogout}>
				<span class="btn-text">Выйти</span>
			</button>
		{:else}
			<a href="/login" class="btn-primary">
				<span class="btn-text">Войти</span>
			</a>
		{/if}
	</div>
</header>

<!-- ПАНЕЛЬ ПОИСКА -->
{#if isSearchOpen}
	<div
		class="search-panel"
		transition:fly={{ y: -20, duration: 300, easing: cubicOut }}
	>
		<div class="search-container">
			<div class="search-input-group">
				<input
					type="text"
					placeholder="Введите поисковый запрос"
					class="search-input"
					bind:value={searchQuery}
					onkeydown={handleSearchKeydown}
				/>
				<button
					class="search-submit-btn"
					onclick={handleSearch}
					aria-label="Поиск"
				>
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
						<circle cx="11" cy="11" r="7" stroke="white" stroke-width="2" />
						<path
							d="M16 16L21 21"
							stroke="white"
							stroke-width="2"
							stroke-linecap="round"
						/>
					</svg>
				</button>
			</div>

			<label class="checkbox-container">
				<Checkbox checked={exactSearch} onchange={v => (exactSearch = v)} />
				<span class="checkbox-text">Точный поиск</span>
			</label>
		</div>
	</div>
	<div
		class="overlay search-overlay"
		onclick={toggleSearch}
		role="button"
		tabindex="0"
		onkeydown={e => e.key === 'Enter' && toggleSearch()}
		transition:fade={{ duration: 200 }}
	></div>
{/if}

<!-- МОБИЛЬНОЕ МЕНЮ -->
{#if isMenuOpen}
	<div class="mobile-menu" transition:fade={{ duration: 200 }}>
		<div class="menu-header">
			<button class="close-btn" onclick={toggleMenu} aria-label="Закрыть меню">
				<svg
					width="32"
					height="32"
					viewBox="0 0 32 32"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M8 8L24 24M24 8L8 24"
						stroke="white"
						stroke-width="2"
						stroke-linecap="round"
					/>
				</svg>
			</button>

			<div class="menu-logo">
				<img src={logoWhiteImg} alt="Логотип" class="logo-img" />
			</div>
		</div>

		<nav class="menu-list">
			{#if $isAdmin}
				<button
					type="button"
					class="menu-item menu-item-admin"
					onclick={toggleAdminMenu}
				>
					<span class="menu-text">Админ</span>
					<svg
						class="caret"
						class:caret-rotated={isAdminMenuOpen}
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
					>
						<path
							d="M6 9L12 15L18 9"
							stroke="white"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
					</svg>
				</button>
				{#if isAdminMenuOpen}
					<div class="admin-submenu">
						<a href="/ste" class="submenu-item" onclick={toggleMenu}>
							<span class="submenu-text">СТЕ</span>
							<span class="arrow">→</span>
						</a>
						<a href="/card" class="submenu-item" onclick={toggleMenu}>
							<span class="submenu-text">Карточки</span>
							<span class="arrow">→</span>
						</a>
					</div>
				{/if}
				<div class="line"></div>
			{/if}

			<a href="/catalog" class="menu-item" onclick={toggleMenu}>
				<span class="menu-text">Каталог</span>
				<span class="arrow">→</span>
			</a>
			<div class="line"></div>

			<button
				type="button"
				class="menu-item menu-item-disabled"
				onclick={e => e.preventDefault()}
			>
				<span class="menu-text">Единый реестр закупок</span>
				<span class="arrow">→</span>
			</button>
			<div class="line"></div>

			<button
				type="button"
				class="menu-item menu-item-disabled"
				onclick={e => e.preventDefault()}
			>
				<span class="menu-text">Контракты</span>
				<span class="arrow">→</span>
			</button>
			<div class="line"></div>

			<button
				type="button"
				class="menu-item menu-item-disabled"
				onclick={e => e.preventDefault()}
			>
				<span class="menu-text">Организации</span>
				<span class="arrow">→</span>
			</button>
			<div class="line"></div>

			<button
				type="button"
				class="menu-item menu-item-disabled"
				onclick={e => e.preventDefault()}
			>
				<span class="menu-text">Дополнительная информация</span>
				<span class="arrow">→</span>
			</button>
			<div class="line"></div>
		</nav>
	</div>
{/if}

<style>
	/* ХЕДЕР */
	.header {
		height: 72px;
		background: white;
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0 160px;
		position: relative;
		z-index: 50;
	}

	.header-left {
		display: flex;
		gap: 24px;
		align-items: center;
	}

	.header-right {
		display: flex;
		gap: 32px;
		align-items: center;
	}

	.menu-btn,
	.search-trigger,
	.close-btn,
	.search-submit-btn {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0;
	}

	.search-trigger {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.search-label {
		font-size: 16px;
		color: #333;
	}

	.btn-primary {
		background: #cd1f15;
		color: white;
		padding: 6px 17px;
		border-radius: 4px;
		text-decoration: none;
	}

	.btn-secondary {
		background: none;
		color: #333;
		padding: 6px 17px;
		border-radius: 4px;
		border: 1px solid #ccc;
		cursor: pointer;
		font-family: inherit;
		font-size: 14px;
	}

	.btn-secondary:hover {
		background: #f5f5f5;
	}

	/* ЛОГОТИП */
	.logo-container {
		display: flex;
		align-items: center;
		height: 40px;
	}

	.logo-img {
		height: 40px;
		width: auto;
		object-fit: contain;
	}

	.menu-logo {
		display: flex;
		align-items: center;
		height: 40px;
	}

	.menu-logo .logo-img {
		height: 40px;
	}

	/* ПОИСК */
	.search-panel {
		position: absolute;
		top: 72px;
		left: 0;
		width: 100%;
		height: 107px;
		background: white;
		z-index: 40;
		display: flex;
		align-items: center;
		padding-left: 160px;
		box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
	}

	.search-container {
		display: flex;
		flex-direction: column;
		gap: 10px;
		width: 100%;
		max-width: 900px;
	}

	.search-input-group {
		display: flex;
		border: 1px solid #ccc;
		height: 44px;
		border-radius: 8px;
		overflow: hidden;
	}

	.search-input {
		flex: 1;
		border: none;
		padding: 0 16px;
		outline: none;
		font-family: inherit;
		font-size: 16px;
	}

	.search-input::placeholder {
		color: #999;
	}

	.search-submit-btn {
		background: #cd1f15;
		width: 54px;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.checkbox-container {
		display: flex;
		gap: 8px;
		font-size: 14px;
		align-items: center;
		cursor: pointer;
	}

	.checkbox-text {
		line-height: 1;
	}

	.search-overlay {
		position: fixed;
		top: 72px;
		left: 0;
		width: 100%;
		height: calc(100vh - 72px);
		background: rgba(2, 1, 1, 0.46);
		z-index: 20;
	}

	/* МОБИЛЬНОЕ МЕНЮ */
	.mobile-menu {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: linear-gradient(223deg, #d73b32 0%, #e65a53 45%, #b95d5d 100%);
		z-index: 100;
		overflow: hidden;
		display: flex;
		flex-direction: column;
	}

	.menu-header {
		display: flex;
		align-items: center;
		height: 72px;
		min-height: 72px;
		flex-shrink: 0;
		padding: 0 160px;
		gap: 24px;
	}

	.close-btn {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
	}

	.menu-list {
		display: flex;
		flex-direction: column;
		width: 100%;
		padding: 0 160px;
		padding-top: 40px;
		padding-bottom: 40px;
		gap: 24px;
		flex: 1;
		overflow-y: auto;
	}

	.menu-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		text-decoration: none;
		color: white;
		cursor: pointer;
		transition: opacity 0.2s;
		background: none;
		border: none;
		padding: 0;
		font-family: inherit;
	}

	.menu-item:hover {
		opacity: 0.8;
	}

	.menu-item-disabled {
		opacity: 0.6;
		cursor: default;
	}

	.menu-item-disabled:hover {
		opacity: 0.6;
	}

	.menu-text {
		font-size: 30px;
		font-weight: 400;
		line-height: 40px;
	}

	.arrow {
		font-size: 24px;
		color: white;
	}

	.line {
		height: 1px;
		background: white;
		opacity: 0.7;
		width: 100%;
	}

	/* Админ подменю */
	.caret {
		transition: transform 0.2s ease;
	}

	.caret-rotated {
		transform: rotate(180deg);
	}

	.admin-submenu {
		display: flex;
		flex-direction: column;
		gap: 16px;
		padding-left: 32px;
		margin-top: 8px;
	}

	.submenu-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		text-decoration: none;
		color: #ffd4d4;
		cursor: pointer;
		transition: opacity 0.2s;
	}

	.submenu-item:hover {
		opacity: 0.8;
	}

	.submenu-text {
		font-size: 24px;
		font-weight: 400;
		line-height: 32px;
	}

	.submenu-item .arrow {
		color: #ffd4d4;
	}

	/* Адаптив */
	@media (max-width: 1200px) {
		.header {
			padding: 0 40px;
		}

		.search-panel {
			padding-left: 40px;
		}

		.menu-header {
			padding: 16px 40px;
		}

		.menu-list {
			padding: 0 40px;
		}
	}

	@media (max-width: 768px) {
		.header {
			padding: 0 16px;
		}

		.search-panel {
			padding-left: 16px;
			padding-right: 16px;
		}

		.menu-header {
			padding: 16px;
		}

		.menu-list {
			padding: 0 16px;
			gap: 20px;
		}

		.menu-text {
			font-size: 20px;
			line-height: 28px;
		}

		.arrow {
			font-size: 20px;
		}
	}

	@media (max-width: 480px) {
		.menu-text {
			font-size: 18px;
			line-height: 24px;
		}

		.menu-list {
			gap: 16px;
		}
	}
</style>
