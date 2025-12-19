<script lang="ts">
	import { getCategories, type Category } from '$lib/api/categories'
	import {
		createSte,
		type SteCharacteristics,
		type SteCreateRequest,
	} from '$lib/api/ste'
	import AuthGuard from '$lib/components/AuthGuard.svelte'
	import Header from '$lib/components/Header.svelte'
	import { onMount } from 'svelte'

	// Form state
	let name = $state('')
	let categoryId = $state<number | null>(null)
	let characteristics = $state<SteCharacteristics>({})

	// New characteristic input
	let newCharKey = $state('')
	let newCharValue = $state('')

	// UI state
	let saving = $state(false)
	let error = $state<string | null>(null)

	// Reference data
	let categories = $state<Category[]>([])
	let categoriesLoading = $state(true)

	onMount(async () => {
		await loadCategories()
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
		if (!categoryId) {
			error = 'Выберите категорию'
			return
		}

		error = null
		saving = true

		try {
			const data: SteCreateRequest = {
				name: name.trim(),
				category_id: categoryId,
				characteristics,
			}
			const created = await createSte(data)
			window.location.href = `/ste/${created.id}`
		} catch (e) {
			console.error('Failed to create STE:', e)
			error = e instanceof Error ? e.message : 'Ошибка при создании СТЕ'
		} finally {
			saving = false
		}
	}
</script>

<svelte:head>
	<title>Добавить СТЕ | TenderHack</title>
</svelte:head>

<AuthGuard requireAdmin>
	<div class="page-wrapper">
		<Header />

		<main class="content">
			<div class="page-header">
				<a href="/ste" class="back-link">
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
				<h1 class="page-title">Добавить СТЕ</h1>
			</div>

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
								placeholder="Введите название товара"
								bind:value={name}
								required
							/>
						</div>

						<div class="form-group">
							<label class="form-label" for="category">Категория *</label>
							<select
								id="category"
								class="form-select"
								bind:value={categoryId}
								required
							>
								<option value={null}>Выберите категорию</option>
								{#each categories as cat}
									<option value={cat.id}>{cat.name}</option>
								{/each}
							</select>
						</div>

						<div class="info-box">
							<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
								<circle
									cx="10"
									cy="10"
									r="8"
									stroke="#666"
									stroke-width="1.5"
								/>
								<path
									d="M10 9V14M10 6V7"
									stroke="#666"
									stroke-width="1.5"
									stroke-linecap="round"
								/>
							</svg>
							<p>
								Для массового импорта СТЕ используйте функцию "Импорт" на
								странице списка СТЕ. Там можно загрузить файл Excel или CSV с
								полными данными товаров.
							</p>
						</div>
					</div>

					<div class="form-section">
						<h2 class="section-title">Характеристики</h2>

						{#if Object.keys(characteristics).length > 0}
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
						{:else}
							<div class="empty-characteristics">
								<p>Характеристики не добавлены</p>
							</div>
						{/if}

						<div class="add-characteristic">
							<input
								type="text"
								class="form-input char-input"
								placeholder="Название характеристики"
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
								aria-label="Добавить характеристику"
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
					<a href="/ste" class="btn-secondary">Отмена</a>
					<button
						type="submit"
						class="btn-primary"
						disabled={saving || !name.trim() || !categoryId}
					>
						{saving ? 'Создание...' : 'Создать СТЕ'}
					</button>
				</div>
			</form>
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

	.info-box {
		display: flex;
		gap: 12px;
		padding: 16px;
		background: #f5f5f5;
		border-radius: 8px;
		margin-top: 8px;
	}

	.info-box svg {
		flex-shrink: 0;
		margin-top: 2px;
	}

	.info-box p {
		font-size: 13px;
		color: #666;
		line-height: 1.5;
		margin: 0;
	}

	.empty-characteristics {
		padding: 32px;
		text-align: center;
		background: #fafafa;
		border-radius: 8px;
		border: 1px dashed #ddd;
	}

	.empty-characteristics p {
		color: #999;
		font-size: 14px;
		margin: 0;
	}

	.characteristics-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
		max-height: 250px;
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
	}
</style>
