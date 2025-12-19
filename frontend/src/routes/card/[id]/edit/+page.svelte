<script lang="ts">
	import { page } from '$app/stores'
	import {
		getCardById,
		updateCard,
		type CardUpdateRequest,
	} from '$lib/api/card'
	import { getAllStes, updateSte, type Ste } from '$lib/api/ste'
	import AuthGuard from '$lib/components/AuthGuard.svelte'
	import Checkbox from '$lib/components/Checkbox.svelte'
	import Header from '$lib/components/Header.svelte'
	import { onMount } from 'svelte'

	// Card edit page - admin only
	let id = $derived($page.params.id)
	let cardId = $derived(parseInt(id))

	// Form state
	let name = $state('')
	let currentSteIds = $state<Set<number>>(new Set())
	let steSearchQuery = $state('')

	// UI state
	let loading = $state(true)
	let saving = $state(false)
	let error = $state<string | null>(null)
	let loadError = $state<string | null>(null)

	// All STEs (both attached and available)
	let allStes = $state<Ste[]>([])
	let stesLoading = $state(true)

	// Filtered STEs: current card's STEs + available STEs without card
	let availableStes = $derived(
		allStes.filter(ste => ste.card_id === cardId || !ste.card_id)
	)

	// Search filter
	let filteredStes = $derived(
		steSearchQuery.trim()
			? availableStes.filter(
					ste =>
						ste.name.toLowerCase().includes(steSearchQuery.toLowerCase()) ||
						ste.model_name
							?.toLowerCase()
							.includes(steSearchQuery.toLowerCase()) ||
						ste.manufacturer
							?.toLowerCase()
							.includes(steSearchQuery.toLowerCase())
				)
			: availableStes
	)

	onMount(async () => {
		await Promise.all([loadCard(), loadStes()])
	})

	async function loadCard() {
		loading = true
		loadError = null
		try {
			const card = await getCardById(cardId)
			name = card.name || ''
			currentSteIds = new Set(card.stes.map(s => s.id))
		} catch (e) {
			console.error('Failed to load card:', e)
			loadError = e instanceof Error ? e.message : 'Ошибка загрузки карточки'
		} finally {
			loading = false
		}
	}

	async function loadStes() {
		stesLoading = true
		try {
			allStes = await getAllStes()
		} catch (e) {
			console.error('Failed to load STEs:', e)
		} finally {
			stesLoading = false
		}
	}

	function toggleSte(steId: number) {
		const newSet = new Set(currentSteIds)
		if (newSet.has(steId)) {
			newSet.delete(steId)
		} else {
			newSet.add(steId)
		}
		currentSteIds = newSet
	}

	function selectAllVisible() {
		const newSet = new Set(currentSteIds)
		for (const ste of filteredStes) {
			newSet.add(ste.id)
		}
		currentSteIds = newSet
	}

	function deselectAll() {
		currentSteIds = new Set()
	}

	async function handleSubmit() {
		error = null
		saving = true

		try {
			// 1. Update card name
			const cardData: CardUpdateRequest = {
				name: name.trim() || undefined,
			}
			await updateCard(cardId, cardData)

			// 2. Update STE associations
			// Get original STEs for this card
			const originalSteIds = new Set(
				allStes.filter(s => s.card_id === cardId).map(s => s.id)
			)

			// Find STEs to add (new ones)
			const stesToAdd = Array.from(currentSteIds).filter(
				id => !originalSteIds.has(id)
			)

			// Find STEs to remove (no longer selected)
			const stesToRemove = Array.from(originalSteIds).filter(
				id => !currentSteIds.has(id)
			)

			// Update STEs: add to card
			for (const steId of stesToAdd) {
				await updateSte(steId, { card_id: cardId })
			}

			// Update STEs: remove from card
			for (const steId of stesToRemove) {
				await updateSte(steId, { card_id: null })
			}

			window.location.href = '/card'
		} catch (e) {
			console.error('Failed to update card:', e)
			error = e instanceof Error ? e.message : 'Ошибка при сохранении карточки'
		} finally {
			saving = false
		}
	}
</script>

<svelte:head>
	<title>Редактирование карточки | TenderHack</title>
</svelte:head>

<AuthGuard requireAuth requireAdmin>
	<div class="page-wrapper">
		<Header />

		<main class="content">
			<div class="page-header">
				<a href="/card" class="back-link">
					<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
						<path
							d="M12.5 15L7.5 10L12.5 5"
							stroke="currentColor"
							stroke-width="1.5"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
					</svg>
					Назад к списку
				</a>
				<h1 class="page-title">Редактирование карточки #{id}</h1>
			</div>

			{#if loading}
				<div class="loading-container">
					<p>Загрузка...</p>
				</div>
			{:else if loadError}
				<div class="error-container">
					<p>{loadError}</p>
					<a href="/card" class="btn-secondary">Вернуться к списку</a>
				</div>
			{:else}
				<form
					class="form-container"
					onsubmit={e => {
						e.preventDefault()
						handleSubmit()
					}}
				>
					{#if error}
						<div class="error-message">{error}</div>
					{/if}

					<div class="form-section">
						<label class="form-label" for="name">Название карточки</label>
						<input
							type="text"
							id="name"
							class="form-input"
							placeholder="Введите название (необязательно)"
							bind:value={name}
						/>
						<p class="form-hint">
							Название будет использоваться для идентификации группы товаров
						</p>
					</div>

					<div class="form-section">
						<div class="section-header">
							<label class="form-label">СТЕ в карточке</label>
							<div class="section-actions">
								<button
									type="button"
									class="btn-text"
									onclick={selectAllVisible}
								>
									Выбрать все
								</button>
								<button type="button" class="btn-text" onclick={deselectAll}>
									Сбросить
								</button>
							</div>
						</div>

						<div class="ste-search">
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
								class="ste-search-input"
								placeholder="Поиск СТЕ по названию, модели или производителю..."
								bind:value={steSearchQuery}
							/>
						</div>

						{#if currentSteIds.size > 0}
							<div class="selected-count">
								Выбрано: {currentSteIds.size} СТЕ
							</div>
						{/if}

						<div class="ste-list">
							{#if stesLoading}
								<div class="loading-state">Загрузка СТЕ...</div>
							{:else if filteredStes.length === 0}
								<div class="empty-state">
									{steSearchQuery ? 'СТЕ не найдены' : 'Нет доступных СТЕ'}
								</div>
							{:else}
								{#each filteredStes as ste}
									<label
										class="ste-item"
										class:selected={currentSteIds.has(ste.id)}
									>
										<Checkbox
											checked={currentSteIds.has(ste.id)}
											onchange={() => toggleSte(ste.id)}
										/>
										<div class="ste-info">
											<div class="ste-name">{ste.name}</div>
											<div class="ste-details">
												{#if ste.model_name}
													<span>Модель: {ste.model_name}</span>
												{/if}
												{#if ste.manufacturer}
													<span>Производитель: {ste.manufacturer}</span>
												{/if}
												{#if ste.category_name}
													<span>Категория: {ste.category_name}</span>
												{/if}
											</div>
										</div>
										{#if ste.image_url}
											<img
												src={ste.image_url}
												alt={ste.name}
												class="ste-image"
											/>
										{/if}
									</label>
								{/each}
							{/if}
						</div>
					</div>

					<div class="form-actions">
						<a href="/card" class="btn-secondary">Отмена</a>
						<button type="submit" class="btn-primary" disabled={saving}>
							{saving ? 'Сохранение...' : 'Сохранить изменения'}
						</button>
					</div>
				</form>
			{/if}
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

	.back-link {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		color: #666;
		text-decoration: none;
		font-size: 14px;
		margin-bottom: 16px;
	}

	.back-link:hover {
		color: #cd1f15;
	}

	.page-title {
		font-size: 32px;
		font-weight: 600;
		color: #333;
		margin: 0;
	}

	.loading-container,
	.error-container {
		background: white;
		border-radius: 12px;
		padding: 60px 40px;
		text-align: center;
	}

	.error-container p {
		color: #cd1f15;
		margin-bottom: 20px;
	}

	.form-container {
		background: white;
		border-radius: 12px;
		padding: 40px;
	}

	.error-message {
		background: #fef2f2;
		color: #cd1f15;
		padding: 12px 16px;
		border-radius: 8px;
		margin-bottom: 24px;
		font-size: 14px;
	}

	.form-section {
		margin-bottom: 32px;
	}

	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 12px;
	}

	.section-actions {
		display: flex;
		gap: 16px;
	}

	.form-label {
		display: block;
		font-size: 14px;
		font-weight: 500;
		color: #333;
		margin-bottom: 8px;
	}

	.section-header .form-label {
		margin-bottom: 0;
	}

	.form-input {
		width: 100%;
		height: 44px;
		padding: 0 16px;
		border: 1px solid #ccc;
		border-radius: 8px;
		font-family: inherit;
		font-size: 14px;
		outline: none;
		box-sizing: border-box;
	}

	.form-input:focus {
		border-color: #cd1f15;
	}

	.form-hint {
		margin-top: 8px;
		font-size: 13px;
		color: #666;
	}

	.btn-text {
		background: none;
		border: none;
		color: #cd1f15;
		font-size: 14px;
		cursor: pointer;
		padding: 0;
	}

	.btn-text:hover {
		text-decoration: underline;
	}

	.ste-search {
		position: relative;
		margin-bottom: 16px;
	}

	.search-icon {
		position: absolute;
		left: 12px;
		top: 50%;
		transform: translateY(-50%);
		pointer-events: none;
	}

	.ste-search-input {
		width: 100%;
		height: 44px;
		padding: 0 16px 0 44px;
		border: 1px solid #ccc;
		border-radius: 8px;
		font-family: inherit;
		font-size: 14px;
		outline: none;
		box-sizing: border-box;
	}

	.ste-search-input:focus {
		border-color: #cd1f15;
	}

	.selected-count {
		background: #e8f5e9;
		color: #2e7d32;
		padding: 8px 16px;
		border-radius: 8px;
		font-size: 14px;
		margin-bottom: 16px;
	}

	.ste-list {
		border: 1px solid #e5e5e5;
		border-radius: 8px;
		max-height: 400px;
		overflow-y: auto;
	}

	.ste-item {
		display: flex;
		align-items: center;
		gap: 16px;
		padding: 16px;
		cursor: pointer;
		border-bottom: 1px solid #e5e5e5;
	}

	.ste-item:last-child {
		border-bottom: none;
	}

	.ste-item:hover {
		background: #fafafa;
	}

	.ste-item.selected {
		background: #fef2f2;
	}

	.ste-info {
		flex: 1;
		min-width: 0;
	}

	.ste-name {
		font-size: 14px;
		font-weight: 500;
		color: #333;
		margin-bottom: 4px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.ste-details {
		display: flex;
		flex-wrap: wrap;
		gap: 12px;
		font-size: 13px;
		color: #666;
	}

	.ste-details span {
		white-space: nowrap;
	}

	.ste-image {
		width: 60px;
		height: 60px;
		object-fit: cover;
		border-radius: 6px;
		flex-shrink: 0;
	}

	.loading-state,
	.empty-state {
		padding: 40px;
		text-align: center;
		color: #666;
		font-size: 14px;
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		gap: 12px;
		padding-top: 24px;
		border-top: 1px solid #e5e5e5;
	}

	.btn-secondary {
		height: 44px;
		padding: 0 24px;
		background: white;
		border: 1px solid #ccc;
		border-radius: 8px;
		font-family: inherit;
		font-size: 14px;
		color: #333;
		cursor: pointer;
		text-decoration: none;
		display: inline-flex;
		align-items: center;
	}

	.btn-secondary:hover {
		background: #f5f5f5;
	}

	.btn-primary {
		height: 44px;
		padding: 0 24px;
		background: #cd1f15;
		border: none;
		border-radius: 8px;
		font-family: inherit;
		font-size: 14px;
		color: white;
		cursor: pointer;
	}

	.btn-primary:hover {
		background: #b81b12;
	}

	.btn-primary:disabled {
		background: #ccc;
		cursor: not-allowed;
	}

	@media (max-width: 1200px) {
		.content {
			padding: 24px 40px 40px;
		}
	}

	@media (max-width: 768px) {
		.content {
			padding: 16px;
		}

		.form-container {
			padding: 24px;
		}

		.section-header {
			flex-direction: column;
			align-items: flex-start;
			gap: 8px;
		}
	}
</style>
