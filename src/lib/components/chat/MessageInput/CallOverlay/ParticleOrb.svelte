<script lang="ts">
	import {
		approach,
		blendEnergy,
		createParticleRenderer,
		createStateMix,
		type OrbState
	} from './particleOrb';

	let {
		state: orbState = 'idle',
		size = 168,
		animated = true,
		level
	}: {
		state?: OrbState;
		size?: number;
		animated?: boolean;
		level?: number;
	} = $props();

	let canvas: HTMLCanvasElement | undefined = $state();
	let wake = () => {};

	$effect(() => {
		if (!canvas) return;

		const render = createParticleRenderer(canvas, size);
		if (!render) return;

		const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
		let mix = createStateMix();
		let previous = 0;
		let phase = 0;
		let energy = 0;
		let frame = 0;
		let visible = true;

		const tick = (now: number) => {
			frame = 0;
			if (!visible || document.hidden) return;
			if (!motion.matches && previous && now - previous < 30) {
				wake();
				return;
			}

			const dt = previous ? Math.min((now - previous) / 1000, 0.1) : 0;
			previous = now;
			if (motion.matches || !animated) {
				mix = createStateMix(orbState);
				energy = 0;
				render(mix.weights, 0, 0);
				return;
			}

			const weights = mix.update(orbState, dt);
			phase += dt;
			const target = level === undefined ? blendEnergy(weights, phase) : level;
			energy = approach(energy, target, target > energy ? 14 : 4, dt);
			render(weights, dt, energy);
			wake();
		};

		wake = () => {
			if (!frame && visible && !document.hidden) frame = requestAnimationFrame(tick);
		};

		function pause() {
			cancelAnimationFrame(frame);
			frame = 0;
			previous = 0;
		}

		function onVisibilityChange() {
			pause();
			wake();
		}

		const observer = new IntersectionObserver(([entry]) => {
			visible = entry.isIntersecting;
			onVisibilityChange();
		});
		observer.observe(canvas);
		document.addEventListener('visibilitychange', onVisibilityChange);
		motion.addEventListener('change', onVisibilityChange);
		wake();

		return () => {
			pause();
			observer.disconnect();
			document.removeEventListener('visibilitychange', onVisibilityChange);
			motion.removeEventListener('change', onVisibilityChange);
			wake = () => {};
		};
	});

	$effect(() => {
		orbState;
		animated;
		wake();
	});
</script>

<canvas
	bind:this={canvas}
	class="pointer-events-none block shrink-0"
	style:width={`${size}px`}
	style:height={`${size}px`}
	aria-hidden="true"
></canvas>
