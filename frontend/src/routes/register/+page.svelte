<script lang="ts">
	import { goto } from '$app/navigation'
	import { ApiError, register } from '$lib/api'
	import { auth } from '$lib/stores/auth'

	let loginValue = $state('')
	let password = $state('')
	let confirmPassword = $state('')
	let showPassword = $state(false)
	let showConfirmPassword = $state(false)
	let isLoading = $state(false)
	let errorMessage = $state('')

	function togglePasswordVisibility() {
		showPassword = !showPassword
	}

	function toggleConfirmPasswordVisibility() {
		showConfirmPassword = !showConfirmPassword
	}

	async function handleRegister() {
		// Валидация
		if (!loginValue.trim() || !password.trim() || !confirmPassword.trim()) {
			errorMessage = 'Заполните все поля'
			return
		}

		if (password !== confirmPassword) {
			errorMessage = 'Пароли не совпадают'
			return
		}

		if (password.length < 6) {
			errorMessage = 'Пароль должен содержать минимум 6 символов'
			return
		}

		isLoading = true
		errorMessage = ''

		try {
			const response = (await register({ login: loginValue, password })) as {
				access_token?: string
			}
			// Если бэкенд возвращает токен после регистрации
			if (response.access_token) {
				auth.setToken(response.access_token)
				goto('/catalog')
			} else {
				// Иначе перенаправляем на страницу входа
				goto('/login')
			}
		} catch (e) {
			if (e instanceof ApiError) {
				if (e.status === 400 || e.status === 409) {
					errorMessage = 'Пользователь с таким логином уже существует'
				} else if (e.status === 422) {
					errorMessage = 'Проверьте правильность введённых данных'
				} else {
					errorMessage = e.data?.detail || 'Ошибка регистрации'
				}
			} else {
				errorMessage = 'Ошибка соединения с сервером'
			}
		} finally {
			isLoading = false
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			handleRegister()
		}
	}

	function goToLogin() {
		goto('/login')
	}
</script>

<svelte:head>
	<title>Регистрация | TenderHack</title>
</svelte:head>

<main class="register-page">
	<div class="register-container">
		<h1 class="register-title">Регистрация</h1>

		{#if errorMessage}
			<div class="error-message">{errorMessage}</div>
		{/if}

		<div class="form-field">
			<label class="field-label" for="login">Логин</label>
			<input
				type="text"
				id="login"
				class="field-input"
				placeholder="Введите логин"
				bind:value={loginValue}
				onkeydown={handleKeydown}
				disabled={isLoading}
			/>
		</div>

		<div class="form-field">
			<label class="field-label" for="password">Пароль</label>
			<div class="password-wrapper">
				<input
					type={showPassword ? 'text' : 'password'}
					id="password"
					class="field-input"
					placeholder="Введите пароль"
					bind:value={password}
					onkeydown={handleKeydown}
					disabled={isLoading}
				/>
				<button
					type="button"
					class="password-toggle"
					onclick={togglePasswordVisibility}
					aria-label={showPassword ? 'Скрыть пароль' : 'Показать пароль'}
				>
					{#if showPassword}
						<svg
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path
								d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
							/>
							<line x1="1" y1="1" x2="23" y2="23" />
						</svg>
					{:else}
						<svg
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
							<circle cx="12" cy="12" r="3" />
						</svg>
					{/if}
				</button>
			</div>
		</div>

		<div class="form-field">
			<label class="field-label" for="confirm-password"
				>Подтвердите пароль</label
			>
			<div class="password-wrapper">
				<input
					type={showConfirmPassword ? 'text' : 'password'}
					id="confirm-password"
					class="field-input"
					placeholder="Повторите пароль"
					bind:value={confirmPassword}
					onkeydown={handleKeydown}
					disabled={isLoading}
				/>
				<button
					type="button"
					class="password-toggle"
					onclick={toggleConfirmPasswordVisibility}
					aria-label={showConfirmPassword ? 'Скрыть пароль' : 'Показать пароль'}
				>
					{#if showConfirmPassword}
						<svg
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path
								d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
							/>
							<line x1="1" y1="1" x2="23" y2="23" />
						</svg>
					{:else}
						<svg
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
							<circle cx="12" cy="12" r="3" />
						</svg>
					{/if}
				</button>
			</div>
		</div>

		<button
			type="button"
			class="btn btn-primary"
			onclick={handleRegister}
			disabled={isLoading}
		>
			{isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
		</button>

		<div class="login-link">
			<span class="login-text">Уже есть аккаунт? </span>
			<button type="button" class="login-button" onclick={goToLogin}>
				Войти
			</button>
		</div>
	</div>
</main>

<style>
	/* ===== Base Styles ===== */
	.register-page {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #f2f2f2;
		font-family: 'Golos Text', sans-serif;
		padding: 20px;
	}

	.register-container {
		width: 100%;
		max-width: 400px;
		background: white;
		border-radius: 8px;
		padding: 40px;
	}

	.register-title {
		color: black;
		font-size: 30px;
		font-weight: 600;
		line-height: 36px;
		margin: 0 0 24px 0;
		text-align: center;
	}

	/* ===== Error Message ===== */
	.error-message {
		background: #fee2e2;
		border: 1px solid #fecaca;
		color: #dc2626;
		padding: 12px 16px;
		border-radius: 4px;
		margin-bottom: 16px;
		font-size: 14px;
		text-align: center;
	}

	/* ===== Form Fields ===== */
	.form-field {
		margin-bottom: 16px;
	}

	.field-label {
		display: block;
		color: #333333;
		font-size: 14px;
		font-weight: 400;
		line-height: 20px;
		margin-bottom: 8px;
	}

	.field-input {
		width: 100%;
		height: 40px;
		padding: 10px 14px;
		background: white;
		border: 1px solid #a7a7ab;
		border-radius: 4px;
		font-family: 'Golos Text', sans-serif;
		font-size: 14px;
		color: black;
		box-sizing: border-box;
		transition:
			border-color 0.2s,
			box-shadow 0.2s;
	}

	.field-input::placeholder {
		color: #76767a;
	}

	.field-input:focus {
		outline: none;
		border-color: #0050b2;
		box-shadow: 0 0 0 2px rgba(0, 80, 178, 0.1);
	}

	.field-input:disabled {
		background: #f5f5f7;
		cursor: not-allowed;
	}

	/* ===== Password Field ===== */
	.password-wrapper {
		position: relative;
	}

	.password-wrapper .field-input {
		padding-right: 44px;
	}

	.password-toggle {
		position: absolute;
		right: 12px;
		top: 50%;
		transform: translateY(-50%);
		background: none;
		border: none;
		cursor: pointer;
		padding: 4px;
		color: #76767a;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color 0.2s;
	}

	.password-toggle:hover {
		color: #333333;
	}

	/* ===== Buttons ===== */
	.btn {
		width: 100%;
		padding: 10px 17px;
		border-radius: 4px;
		font-family: 'Golos Text', sans-serif;
		font-size: 14px;
		font-weight: 400;
		line-height: 20px;
		cursor: pointer;
		border: none;
		transition:
			background-color 0.2s,
			opacity 0.2s;
	}

	.btn:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.btn-primary {
		background: #cd1f15;
		color: white;
		margin-bottom: 24px;
	}

	.btn-primary:hover:not(:disabled) {
		background: #b31a12;
	}

	/* ===== Login Link ===== */
	.login-link {
		text-align: center;
	}

	.login-text {
		color: #333333;
		font-size: 14px;
		font-weight: 400;
		line-height: 20px;
	}

	.login-button {
		background: none;
		border: none;
		color: #0050b2;
		font-family: 'Golos Text', sans-serif;
		font-size: 14px;
		font-weight: 400;
		line-height: 20px;
		cursor: pointer;
		padding: 0;
	}

	.login-button:hover {
		text-decoration: underline;
	}
</style>
