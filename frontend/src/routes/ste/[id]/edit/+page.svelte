<script lang="ts">
	import { page } from '$app/stores'
	import { getCardList, type Card } from '$lib/api/card'
	import { getCategories, type Category } from '$lib/api/categories'
	import {
		getSteById,
		updateSte,
		type SteCharacteristics,
		type SteUpdateRequest,
	} from '$lib/api/ste'
	import AuthGuard from '$lib/components/AuthGuard.svelte'
	import Header from '$lib/components/Header.svelte'
	import { onMount } from 'svelte'

	let id = $derived($page.params.id)
	let steId = $derived(parseInt(id))

	// Form state
	let name = $state('')
	let modelName = $state('')
	let manufacturer = $state('')
	let countryOfOrigin = $state('')
	let categoryId = $state<number | null>(null)
	let cardId = $state<number | null>(null)
	let characteristics = $state<SteCharacteristics>({})

	// New characteristic input
	let newCharKey = $state('')
	let newCharValue = $state('')

	// UI state
	let loading = $state(true)
	let saving = $state(false)
	let error = $state<string | null>(null)
	let loadError = $state<string | null>(null)

	// Reference data
	let categories = $state<Category[]>([])
	let cards = $state<Card[]>([])

	onMount(async () => {
		await Promise.all([loadSte(), loadCategories(), loadCards()])
	})

	async function loadSte() {
		loading = true
		loadError = null
		try {
			const ste = await getSteById(steId)
			name = ste.name
			modelName = ste.model_name || ''
			manufacturer = ste.manufacturer || ''
			countryOfOrigin = ste.country_of_origin || ''
			categoryId = ste.category_id
			cardId = ste.card_id || null
			characteristics = { ...ste.characteristics }
		} catch (e) {
			console.error('Failed to load STE:', e)
			loadError = e instanceof Error ? e.message : 'Ошибка загрузки СТЕ'
		} finally {
			loading = false
		}
	}

	async function loadCategories() {
		try {
			categories = await getCategories()
		} catch (e) {
			console.error('Failed to load categories:', e)
		}
	}

	async function loadCards() {
		try {
			cards = await getCardList()
		} catch (e) {
			console.error('Failed to load cards:', e)
		}
	}

	function addCharacteristic() {
		if (newCharKey.trim() && newCharValue.trim()) {
			characteristics = {
				...characteristics,
				[newCharKey.trim()]: newCharValue.trim(),
			}
			newCharKey = ''
			newCharValue = ''
		}
	}

	function removeCharacteristic(key: string) {
		const { [key]: _, ...rest } = characteristics
		characteristics = rest
	}

	async function handleSubmit() {
		error = null
		saving = true

		try {
			const data: SteUpdateRequest = {
				name: name.trim(),
				characteristics,
				card_id: cardId,
			}
			await updateSte(steId, data)
			window.location.href = `/ste/${steId}`
		} catch (e) {
			console.error('Failed to update STE:', e)
			error = e instanceof Error ? e.message : 'Ошибка при сохранении'
		} finally {
			saving = false
		}
	}
</script>

<svelte:head>
	<title>Редактирование СТЕ | TenderHack</title>
</svelte:head>

<AuthGuard requireAuth requireAdmin>
	<div class="page-wrapper">
		<Header />

		<main class="content">
			<div class="page-header">
				<a href="/ste/{id}" class="back-link">
					<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
						<path
							d="M12.5 15L7.5 10L12.5 5"
							stroke="currentColor"
							stroke-width="1.5"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
					</svg>
					Назад к СТЕ
				</a>
				<h1 class="page-title">Редактирование СТЕ #{id}</h1>
			</div>

			{#if loading}
				<div class="loading-container">
					<p>Загрузка...</p>
				</div>
			{:else if loadError}
				<div class="error-container">
					<p>{loadError}</p>
					<a href="/ste" class="btn-secondary">Вернуться к списку</a>
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

					<div class="form-grid">
						<div class="form-section">
							<h2 class="section-title">Основная информация</h2>

							<div class="form-group">
								<label class="form-label" for="name">Название *</label>
								<input
									type="text"
									id="name"
									class="form-input"
									placeholder="Введите название"
									bind:value={name}
									required
								/>
							</div>

							<div class="form-row">
								<div class="form-group">
									<label class="form-label" for="modelName">Модель</label>
									<input
										type="text"
										id="modelName"
										class="form-input"
										placeholder="Модель товара"
										bind:value={modelName}
										disabled
									/>
									<p class="form-hint">Поле только для чтения</p>
								</div>

								<div class="form-group">
									<label class="form-label" for="manufacturer"
										>Производитель</label
									>
									<input
										type="text"
										id="manufacturer"
										class="form-input"
										placeholder="Производитель"
										bind:value={manufacturer}
										disabled
									/>
									<p class="form-hint">Поле только для чтения</p>
								</div>
							</div>

							<div class="form-row">
								<div class="form-group">
									<label class="form-label" for="country"
										>Страна происхождения</label
									>
									<input
										type="text"
										id="country"
										class="form-input"
										placeholder="Страна"
										bind:value={countryOfOrigin}
										disabled
									/>
									<p class="form-hint">Поле только для чтения</p>
								</div>

								<div class="form-group">
									<label class="form-label" for="category">Категория</label>
									<select
										id="category"
										class="form-select"
										bind:value={categoryId}
										disabled
									>
										<option value={null}>Не выбрана</option>
										{#each categories as cat}
											<option value={cat.id}>{cat.name}</option>
										{/each}
									</select>
									<p class="form-hint">Поле только для чтения</p>
								</div>
							</div>

							<div class="form-group">
								<label class="form-label" for="card">Привязка к карточке</label>
								<select id="card" class="form-select" bind:value={cardId}>
									<option value={null}>Не привязан</option>
									{#each cards as card}
										<option value={card.id}>
											#{card.id} - {card.name || 'Без названия'}
										</option>
									{/each}
								</select>
							</div>
						</div>

						<div class="form-section">
							<h2 class="section-title">Характеристики</h2>

							<div class="characteristics-list">
								{#each Object.entries(characteristics) as [key, value]}
									<div class="characteristic-row">
										<span class="char-key">{key}</span>
										<span class="char-value">{value}</span>
										<button
											type="button"
											class="btn-remove"
											onclick={() => removeCharacteristic(key)}
											title="Удалить"
										>
											<svg
												width="16"
												height="16"
												viewBox="0 0 16 16"
												fill="none"
											>
												<path
													d="M12 4L4 12M4 4L12 12"
													stroke="currentColor"
													stroke-width="1.5"
													stroke-linecap="round"
												/>
											</svg>
										</button>
									</div>
								{/each}
							</div>

							<div class="add-characteristic">
								<input
									type="text"
									class="form-input char-input"
									placeholder="Название"
									bind:value={newCharKey}
								/>
								<input
									type="text"
									class="form-input char-input"
									placeholder="Значение"
									bind:value={newCharValue}
								/>
								<button
									type="button"
									class="btn-add"
									onclick={addCharacteristic}
									disabled={!newCharKey.trim() || !newCharValue.trim()}
								>
									<svg width="18" height="18" viewBox="0 0 18 18" fill="none">
										<path
											d="M9 3.75V14.25M3.75 9H14.25"
											stroke="currentColor"
											stroke-width="1.5"
											stroke-linecap="round"
										/>
									</svg>
								</button>
							</div>
						</div>
					</div>

					<div class="form-actions">
						<a href="/ste/{id}" class="btn-secondary">Отмена</a>
						<button
							type="submit"
							class="btn-primary"
							disabled={saving || !name.trim()}
						>
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

	.form-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 32px;
	}

	.form-section {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.section-title {
		font-size: 18px;
		font-weight: 600;
		color: #333;
		margin: 0 0 8px;
		padding-bottom: 12px;
		border-bottom: 1px solid #e5e5e5;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 16px;
	}

	.form-label {
		font-size: 14px;
		font-weight: 500;
		color: #333;
	}

	.form-input,
	.form-select {
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

	.form-input:focus,
	.form-select:focus {
		border-color: #cd1f15;
	}

	.form-input:disabled,
	.form-select:disabled {
		background: #f5f5f5;
		color: #666;
		cursor: not-allowed;
	}

	.form-hint {
		font-size: 12px;
		color: #999;
		margin: 0;
	}

	.characteristics-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
		max-height: 300px;
		overflow-y: auto;
	}

	.characteristic-row {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 10px 14px;
		background: #fafafa;
		border-radius: 8px;
	}

	.char-key {
		flex: 1;
		font-size: 14px;
		color: #666;
	}

	.char-value {
		flex: 1;
		font-size: 14px;
		font-weight: 500;
		color: #333;
	}

	.btn-remove {
		width: 28px;
		height: 28px;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		background: transparent;
		border: none;
		border-radius: 4px;
		color: #999;
		cursor: pointer;
	}

	.btn-remove:hover {
		background: #fee;
		color: #cd1f15;
	}

	.add-characteristic {
		display: flex;
		gap: 8px;
		margin-top: 12px;
	}

	.char-input {
		flex: 1;
	}

	.btn-add {
		width: 44px;
		height: 44px;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #cd1f15;
		border: none;
		border-radius: 8px;
		color: white;
		cursor: pointer;
		flex-shrink: 0;
	}

	.btn-add:hover {
		background: #b81b12;
	}

	.btn-add:disabled {
		background: #ccc;
		cursor: not-allowed;
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		gap: 12px;
		padding-top: 32px;
		margin-top: 32px;
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

	@media (max-width: 900px) {
		.form-grid {
			grid-template-columns: 1fr;
		}
	}

	@media (max-width: 768px) {
		.content {
			padding: 16px;
		}

		.form-container {
			padding: 24px;
		}

		.form-row {
			grid-template-columns: 1fr;
		}
	}
</style>
