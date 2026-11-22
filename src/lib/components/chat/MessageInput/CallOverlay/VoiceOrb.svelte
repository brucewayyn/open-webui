<script lang="ts">
	let {
		level = 0,
		muted = false,
		speaking = false
	}: { level?: number; muted?: boolean; speaking?: boolean } = $props();

	const energy = $derived(
		muted || !Number.isFinite(level)
			? 0
			: Math.min(1, Math.max(0, level * (speaking ? 12 : 6))) ** 0.75
	);
</script>

<span
	class="orb relative block aspect-square w-28 rounded-full"
	class:muted
	class:speaking
	style:--energy={energy}
	aria-hidden="true"
>
	<span class="surface absolute inset-0 overflow-hidden rounded-full"></span>
</span>

<style>
	.orb {
		transform: scale(calc(1 + var(--energy) * 0.22));
		box-shadow: 0 0 calc(18px + var(--energy) * 32px)
			rgb(91 100 255 / calc(0.24 + var(--energy) * 0.35));
		transition: transform 110ms ease-out, box-shadow 150ms ease-out, opacity 180ms ease;
	}
	.surface {
		isolation: isolate;
		background: #292180;
	}
	.surface::before,
	.surface::after {
		content: '';
		position: absolute;
		pointer-events: none;
	}
	.surface::before {
		inset: -45%;
		background:
			radial-gradient(ellipse at 32% 28%, #b4ffee, transparent 34%),
			radial-gradient(ellipse at 68% 40%, #aa91ff, transparent 36%),
			radial-gradient(ellipse at 53% 77%, #37cfe1, transparent 40%),
			conic-gradient(from 24deg, #4830ae, #456fff, #863edd, #28206f, #4830ae);
		filter: saturate(calc(1 + var(--energy) * 0.35));
		animation: flow 9s ease-in-out infinite alternate;
	}
	.surface::after {
		inset: 0;
		border-radius: inherit;
		background:
			radial-gradient(ellipse at 33% 19%, rgb(229 255 255 / 48%), transparent 50%),
			radial-gradient(ellipse at 40% 34%, transparent 37%, rgb(15 9 67 / 65%) 100%);
		box-shadow: inset 0 0 0 1px rgb(222 237 255 / 23%);
	}
	.speaking .surface::after {
		background:
			radial-gradient(ellipse at 38% 24%, rgb(234 243 255 / 65%), transparent 57%),
			radial-gradient(ellipse at 40% 34%, transparent 44%, rgb(15 9 67 / 55%) 100%);
	}
	.muted {
		opacity: 0.58;
	}
	.muted .surface::before {
		animation-play-state: paused;
	}
	@keyframes flow {
		0% {
			transform: translate(-8%, -5%) rotate(-27deg);
		}
		48% {
			transform: translate(10%, 4%) rotate(49deg);
		}
		100% {
			transform: translate(-4%, 10%) rotate(130deg);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.orb {
			transform: none;
			transition: none;
		}
		.surface::before {
			animation: none;
		}
	}
</style>
