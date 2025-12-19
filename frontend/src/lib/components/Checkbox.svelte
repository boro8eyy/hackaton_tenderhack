<script lang="ts">
	interface Props {
		checked?: boolean
		onchange?: (checked: boolean) => void
		disabled?: boolean
	}

	let { checked = false, onchange, disabled = false }: Props = $props()

	function handleChange(event: Event) {
		const target = event.target as HTMLInputElement
		onchange?.(target.checked)
	}
</script>

<label class="checkbox-wrapper" class:disabled>
	<input
		type="checkbox"
		{checked}
		{disabled}
		onchange={handleChange}
		class="checkbox-input"
	/>
	<span class="checkbox-custom">
		{#if checked}
			<svg width="12" height="10" viewBox="0 0 12 10" fill="none">
				<path
					d="M1 5L4.5 8.5L11 1.5"
					stroke="white"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		{/if}
	</span>
</label>

<style>
	.checkbox-wrapper {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
	}

	.checkbox-wrapper.disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	.checkbox-input {
		position: absolute;
		opacity: 0;
		width: 0;
		height: 0;
		pointer-events: none;
	}

	.checkbox-custom {
		width: 20px;
		height: 20px;
		border: 2px solid #b0abab;
		border-radius: 4px;
		background: white;
		display: flex;
		align-items: center;
		justify-content: center;
		/* flex-shrink: 0; */
	}

	.checkbox-input:checked + .checkbox-custom {
		background: #cd1f15;
		border-color: #cd1f15;
	}

	.checkbox-wrapper:hover .checkbox-custom {
		border-color: #cd1f15;
	}

	.checkbox-input:focus + .checkbox-custom {
		box-shadow: 0 0 0 2px rgba(205, 31, 21, 0.2);
	}
</style>
