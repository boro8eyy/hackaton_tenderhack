<script lang="ts">
	import { deleteCard, getCardList, type Card } from '$lib/api/card'
	import { getCategories, type Category } from '$lib/api/categories'
	import AuthGuard from '$lib/components/AuthGuard.svelte'
	import Checkbox from '$lib/components/Checkbox.svelte'
	import Header from '$lib/components/Header.svelte'
	import { onMount } from 'svelte'

	// Card list page - admin only

	let searchQuery = $state('')
	let selectedCategories = $state<number[]>([])
	let selectedItems = $state<Set<number>>(new Set())
	let selectAll = $state(false)
	let isCategoryDropdownOpen = $state(false)

	// Категории из API
	let categories = $state<Category[]>([])
	let categoriesLoading = $state(true)

	// Card данные из API
	let cardItems = $state<Card[]>([])
	let cardLoading = $state(true)
	let cardError = $state<string | null>(null)

	// Computed: есть ли выбранные элементы
	let hasSelection = $derived(selectedItems.size > 0)
	let isSingleSelection = $derived(selectedItems.size === 1)

	onMount(async () => {
		await Promise.all([loadCategories(), loadCardItems()])
	})

	async function loadCategories() {
		try {
			categories = await getCategories()
		} catch (e) {
			console.error('Failed to load categories:', e)
		} finally {
			categoriesLoading = false
		}
	}

	async function loadCardItems() {
		cardLoading = true
		cardError = null
		try {
			cardItems = await getCardList(
				searchQuery || undefined,
				selectedCategories.length > 0 ? selectedCategories : undefined
			)
		} catch (e) {
			console.error('Failed to load card items:', e)
			cardError = e instanceof Error ? e.message : 'Ошибка загрузки данных'
		} finally {
			cardLoading = false
		}
	}

	function toggleSelectAll() {
		if (selectAll) {
			selectedItems = new Set()
		} else {
			selectedItems = new Set(cardItems.map(item => item.id))
		}
		selectAll = !selectAll
	}

	function toggleItem(cardId: number) {
		const newSet = new Set(selectedItems)
		if (newSet.has(cardId)) {
			newSet.delete(cardId)
		} else {
			newSet.add(cardId)
		}
		selectedItems = newSet
		selectAll = newSet.size === cardItems.length
	}

	function toggleCategory(categoryId: number) {
		if (selectedCategories.includes(categoryId)) {
			selectedCategories = selectedCategories.filter(id => id !== categoryId)
		} else {
			selectedCategories = [...selectedCategories, categoryId]
		}
		// Перезагружаем данные при изменении фильтра
		loadCardItems()
	}

	async function deleteSelected() {
		if (!confirm(`Удалить ${selectedItems.size} карточек?`)) return

		try {
			for (const id of selectedItems) {
				await deleteCard(id)
			}
			selectedItems = new Set()
			selectAll = false
			await loadCardItems()
		} catch (e) {
			console.error('Failed to delete:', e)
			alert('Ошибка при удалении')
		}
	}

	function reaggregateSelected() {
		// TODO: Implement reaggregate API call
		console.log('Reaggregate:', Array.from(selectedItems))
	}

	function editSelected() {
		const cardId = Array.from(selectedItems)[0]
		window.location.href = `/card/${cardId}/edit`
	}

	// Поиск по нажатию Enter
	function handleSearchKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			loadCardItems()
		}
	}

	/* Mock data for testing - закомментировано, используем API
	const cardItems = [
		{
			card_id: '2001',
			image:
				'https://zakupki.mos.ru/newapi/api/Core/Thumbnail/1856079950/300/300',
			model: 'X1502ZA',
			products_count: 15,
			features: 'Процессор: Intel Core i5, ОЗУ: 8 ГБ, SSD: 512 ГБ',
		},
		{
			card_id: '2002',
			image: null,
			model: 'S27F350',
			products_count: 8,
			features: 'Диагональ: 27", Разрешение: Full HD, Матрица: IPS',
		},
		{
			card_id: '2003',
			image: null,
			model: 'K380',
			products_count: 23,
			features: 'Тип: беспроводная, Подключение: Bluetooth',
		},
		{
			card_id: '2004',
			image: null,
			model: 'XMWXSB02YM',
			products_count: 42,
			features: 'Тип: беспроводная, Сенсор: оптический',
		},
		{
			card_id: '2005',
			image: null,
			model: 'M111w',
			products_count: 5,
			features: 'Тип: лазерный, Формат: A4, Wi-Fi: есть',
		},
	]
	*/
</script>

<svelte:head>
	<title>Карточки | TenderHack</title>
</svelte:head>

<!-- TODO: на проде вернуть requireAuth -->
<AuthGuard requireAdmin>
	<div class="page-wrapper">
		<Header />

		<main class="content">
			<div class="page-header">
				<h1 class="page-title">Список агрегированных СТЕ</h1>
			</div>

			<!-- Панель управления -->
			<div class="controls">
				<div class="controls-left">
					<div class="search-box">
						<svg
							class="search-icon"
							width="20"
							height="20"
							viewBox="0 0 20 20"
							fill="none"
						>
							<path
								d="M17.5 17.5L13.875 13.875M15.8333 9.16667C15.8333 12.8486 12.8486 15.8333 9.16667 15.8333C5.48477 15.8333 2.5 12.8486 2.5 9.16667C2.5 5.48477 5.48477 2.5 9.16667 2.5C12.8486 2.5 15.8333 5.48477 15.8333 9.16667Z"
								stroke="#76767A"
								stroke-width="1.5"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
						</svg>
						<input
							type="text"
							placeholder="Поиск..."
							class="search-input"
							bind:value={searchQuery}
							onkeydown={handleSearchKeydown}
						/>
					</div>

					<div class="category-dropdown">
						<button
							class="btn-secondary category-btn"
							onclick={() => (isCategoryDropdownOpen = !isCategoryDropdownOpen)}
						>
							<span
								>Категории{selectedCategories.length > 0
									? ` (${selectedCategories.length})`
									: ''}</span
							>
							<svg
								class="dropdown-icon"
								class:open={isCategoryDropdownOpen}
								width="16"
								height="16"
								viewBox="0 0 16 16"
								fill="none"
							>
								<path
									d="M4 6L8 10L12 6"
									stroke="currentColor"
									stroke-width="1.5"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</button>
						{#if isCategoryDropdownOpen}
							<div class="category-menu">
								{#each categories as category}
									<label class="category-item">
										<Checkbox
											checked={selectedCategories.includes(category.id)}
											onchange={() => toggleCategory(category.id)}
										/>
										<span class="category-name">{category.name}</span>
									</label>
								{/each}
							</div>
						{/if}
					</div>
				</div>

				<div class="controls-right">
					{#if hasSelection}
						<button class="btn-secondary" onclick={reaggregateSelected}>
							<svg width="18" height="18" viewBox="0 0 18 18" fill="none">
								<path
									d="M1.5 9C1.5 13.1421 4.85786 16.5 9 16.5C13.1421 16.5 16.5 13.1421 16.5 9C16.5 4.85786 13.1421 1.5 9 1.5C6.17157 1.5 3.69396 3.08579 2.38071 5.43934M2.38071 5.43934V2.25M2.38071 5.43934H5.56934"
									stroke="currentColor"
									stroke-width="1.5"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
							Переагрегировать
						</button>
						{#if isSingleSelection}
							<button class="btn-secondary" onclick={editSelected}>
								<svg width="18" height="18" viewBox="0 0 18 18" fill="none">
									<path
										d="M12.75 2.25L15.75 5.25M1.5 16.5L2.25 13.125L13.5 1.875C13.6989 1.67606 13.9348 1.51778 14.1947 1.40915C14.4546 1.30052 14.7333 1.24371 15.0149 1.24197C15.2965 1.24022 15.5759 1.29357 15.8372 1.39898C16.0984 1.50439 16.3362 1.6597 16.5377 1.85723C16.7392 2.05475 16.8994 2.28955 17.0099 2.54853C17.1204 2.80751 17.1788 3.08543 17.1819 3.36694C17.185 3.64845 17.1328 3.9277 17.0281 4.18904C16.9234 4.45038 16.7686 4.68852 16.5729 4.89L5.25 16.125L1.5 16.5Z"
										stroke="currentColor"
										stroke-width="1.5"
										stroke-linecap="round"
										stroke-linejoin="round"
									/>
								</svg>
								Изменить
							</button>
						{/if}
						<button
							class="btn-icon btn-danger"
							onclick={deleteSelected}
							title="Удалить выбранные"
						>
							<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
								<path
									d="M2.5 5H4.16667M4.16667 5H17.5M4.16667 5V16.6667C4.16667 17.1087 4.34226 17.5326 4.65482 17.8452C4.96738 18.1577 5.39131 18.3333 5.83333 18.3333H14.1667C14.6087 18.3333 15.0326 18.1577 15.3452 17.8452C15.6577 17.5326 15.8333 17.1087 15.8333 16.6667V5H4.16667ZM6.66667 5V3.33333C6.66667 2.89131 6.84226 2.46738 7.15482 2.15482C7.46738 1.84226 7.89131 1.66667 8.33333 1.66667H11.6667C12.1087 1.66667 12.5326 1.84226 12.8452 2.15482C13.1577 2.46738 13.3333 2.89131 13.3333 3.33333V5M8.33333 9.16667V14.1667M11.6667 9.16667V14.1667"
									stroke="currentColor"
									stroke-width="1.5"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</button>
					{:else}
						<a href="/card/new" class="btn-secondary">
							<svg width="18" height="18" viewBox="0 0 18 18" fill="none">
								<path
									d="M9 3.75V14.25M3.75 9H14.25"
									stroke="currentColor"
									stroke-width="1.5"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
							Добавить карточку
						</a>
					{/if}
				</div>
			</div>

			<!-- Таблица -->
			<div class="table-container">
				<table class="data-table">
					<thead>
						<tr>
							<th class="col-checkbox">
								<Checkbox checked={selectAll} onchange={toggleSelectAll} />
							</th>
							<th class="col-card-id">ID</th>
							<th class="col-image">Фото</th>
							<th class="col-name">Название</th>
							<th class="col-count">Кол-во товаров</th>
							<th class="col-features">Значимые характеристики</th>
						</tr>
					</thead>
					<tbody>
						{#if cardLoading}
							<tr>
								<td colspan="6" class="loading-cell">Загрузка...</td>
							</tr>
						{:else if cardError}
							<tr>
								<td colspan="6" class="error-cell">{cardError}</td>
							</tr>
						{:else if cardItems.length === 0}
							<tr>
								<td colspan="6" class="empty-cell">Нет данных</td>
							</tr>
						{:else}
							{#each cardItems as item}
								<tr>
									<td class="col-checkbox">
										<Checkbox
											checked={selectedItems.has(item.id)}
											onchange={() => toggleItem(item.id)}
										/>
									</td>
									<td class="col-card-id">
										<a href="/card/{item.id}" class="table-link">{item.id}</a>
									</td>
									<td class="col-image">
										<!-- У Card нет отдельного image_url, используем первое STE если есть -->
										{#if item.stes && item.stes.length > 0 && item.stes[0].image_url}
											<img
												src={item.stes[0].image_url}
												alt={item.name || 'Карточка'}
												class="table-image"
											/>
										{:else}
											<span class="no-image">—</span>
										{/if}
									</td>
									<td class="col-name">{item.name || '—'}</td>
									<td class="col-count">{item.stes?.length || 0}</td>
									<td class="col-features">
										<!-- Выводим характеристики первого STE -->
										{#if item.stes && item.stes.length > 0 && item.stes[0].characteristics}
											{Object.entries(item.stes[0].characteristics)
												.slice(0, 3)
												.map(([k, v]) => `${k}: ${v}`)
												.join(', ')}
										{:else}
											—
										{/if}
									</td>
								</tr>
							{/each}
						{/if}
					</tbody>
				</table>
			</div>
		</main>
	</div>
</AuthGuard>

<style>
	.page-wrapper {
		background-color: #f2f2f2;
		min-height: 100vh;
	}

	.content {
		padding: 24px 160px 40px;
		max-width: 1440px;
		margin: 0 auto;
	}

	.page-header {
		margin-bottom: 24px;
	}

	.page-title {
		font-size: 32px;
		font-weight: 600;
		color: #333;
		margin: 0;
	}

	/* Панель управления */
	.controls {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 16px;
		margin-bottom: 24px;
		flex-wrap: wrap;
	}

	.controls-left {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.controls-right {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.search-box {
		position: relative;
		width: 280px;
	}

	.search-icon {
		position: absolute;
		left: 12px;
		top: 50%;
		transform: translateY(-50%);
		pointer-events: none;
	}

	.search-input {
		width: 100%;
		height: 40px;
		padding: 0 12px 0 40px;
		border: 1px solid #aaa;
		border-radius: 7px;
		font-family: inherit;
		font-size: 14px;
		outline: none;
	}

	.search-input:focus {
		border-color: #cd1f15;
	}

	.category-dropdown {
		position: relative;
	}

	.category-btn {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.dropdown-icon {
		transition: transform 0.2s ease;
	}

	.dropdown-icon.open {
		transform: rotate(180deg);
	}

	.category-menu {
		position: absolute;
		top: calc(100% + 4px);
		left: 0;
		background: white;
		border-radius: 8px;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
		padding: 8px 0;
		min-width: 200px;
		z-index: 100;
	}

	.category-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 10px 16px;
		cursor: pointer;
	}

	.category-item:hover {
		background: #f5f5f5;
	}

	.category-name {
		font-size: 14px;
		color: #333;
	}

	.btn-secondary {
		height: 40px;
		padding: 0 20px;
		background: white;
		border: none;
		border-radius: 7px;
		font-family: inherit;
		font-size: 14px;
		color: #333;
		cursor: pointer;
		white-space: nowrap;
		display: flex;
		align-items: center;
		gap: 8px;
		text-decoration: none;
	}

	.btn-secondary:hover {
		background: #f5f5f5;
	}

	.btn-secondary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.btn-icon {
		width: 40px;
		height: 40px;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		background: white;
		border: none;
		border-radius: 7px;
		cursor: pointer;
	}

	.btn-icon:hover {
		background: #f5f5f5;
	}

	.btn-danger {
		color: #cd1f15;
	}

	.btn-danger:hover {
		background: #fef2f2;
	}

	/* Таблица */
	.table-container {
		background: white;
		border-radius: 12px;
		overflow: hidden;
	}

	.data-table {
		width: 100%;
		border-collapse: collapse;
	}

	.data-table th,
	.data-table td {
		padding: 16px 20px;
		text-align: left;
		border: 1px solid #e5e5e5;
	}

	.data-table th {
		background: #f5f5f5;
		font-weight: 500;
		color: #333;
		font-size: 14px;
	}

	.data-table td {
		font-size: 14px;
		color: #333;
	}

	.data-table tbody tr:hover {
		background: #fafafa;
	}

	.col-card-id {
		width: 80px;
	}

	.table-link {
		color: #cd1f15;
		text-decoration: none;
		font-weight: 500;
	}

	.table-link:hover {
		text-decoration: underline;
	}

	.col-image {
		width: 92px;
		text-align: center;
		padding: 0 !important;
	}

	.col-name {
		width: 200px;
	}

	.col-count {
		width: 120px;
		text-align: center;
	}

	.col-features {
		min-width: 250px;
	}

	.col-checkbox {
		width: 50px;
		text-align: center;
	}

	.table-image {
		width: 100%;
		height: 76px;
		object-fit: cover;
		display: block;
	}

	.no-image {
		color: #999;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 76px;
	}

	.loading-cell,
	.error-cell,
	.empty-cell {
		text-align: center;
		padding: 40px !important;
		color: #666;
	}

	.error-cell {
		color: #cd1f15;
	}

	/* Responsive */
	@media (max-width: 1200px) {
		.content {
			padding: 24px 40px 40px;
		}
	}

	@media (max-width: 768px) {
		.content {
			padding: 16px;
		}

		.controls {
			flex-direction: column;
		}

		.search-box {
			min-width: 100%;
		}

		.table-container {
			overflow-x: auto;
		}
	}
</style>
