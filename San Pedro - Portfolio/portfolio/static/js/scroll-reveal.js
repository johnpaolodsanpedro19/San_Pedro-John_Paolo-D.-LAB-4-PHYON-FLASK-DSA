const revealItems = document.querySelectorAll('[data-scroll-reveal]');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (revealItems.length && !reducedMotion && 'IntersectionObserver' in window) {
    document.body.classList.add('has-scroll-reveal');

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -35px 0px'
    });

    revealItems.forEach((item) => revealObserver.observe(item));
}
