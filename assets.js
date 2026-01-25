class MySidebar extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <nav class="nav">
        <a href="/index.html">home</a>
        <a href="/about.html">about</a>
        <a href="/book.html">book</a>
        <a href="/blog.html">blog</a>
        <a href="/photography.html">photography</a>
        <a href="/contact.html">contact</a>
      </nav>
    `;
  }
}
customElements.define('main-nav', MySidebar);

const headContent = `
    <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <title>Vitez Engineering</title>
  <link rel="icon" type="image/png" href="/logo-small-square.png">
`;

document.head.insertAdjacentHTML('beforeend', headContent);

const blogPosts = [
    { url: "/blog-post/re.html", title: "On the Responsible Engineer Model" },
    { url: "/blog-post/torture.html", title: "Torturing Terrorist" },
    { url: "/blog-post/bike-commuting.html", title: "Bike Commuting: You don't have a good excuse" },
    { url: "/blog-post/10-precepts.html", title: "My Ten Precepts" },
    { url: "/blog-post/happiness.html", title: "Happiness, Equanimity, and the Meaning of it all" },
    { url: "/blog-post/self-improvement.html", title: "Get Back On The Horse, At Dawn We Ride" },
    { url: "/blog-post/humes-problem.html", title: "Science Isn't Irrational: On Hume's Problem of Induction" },
    { url: "/blog-post/gay-engineer.html", title: "On Being a Gay Engineer" },
    { url: "/blog-post/llm-in-engineering.html", title: "Large Language Models in Serious Engineering Applications" },
    { url: "/blog-post/listening.html", title: "Be The One Who Listens" }
];

window.addEventListener('DOMContentLoaded', () => {

    // Prevent browser scroll restoration on refresh
    if ('scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
    }
    
    // Force scroll to top on page load
    window.scrollTo(0, 0);

    // Optimized parallax effect on scroll
    let ticking = false;
    let animationsDisabled = false;
    let scrollEffectsEnabled = false;
    const hasHero = document.querySelector('.hero') !== null;
    let animationCleanupTimer = null;
    
    // Function to clean up animations and enable scroll effects
    const enableScrollEffects = () => {
        if (scrollEffectsEnabled) return; // Already enabled
        
        const logo = document.querySelector('.hero > .logo-container');
        const title = document.querySelector('.hero > .hero-title');
        const subtitle = document.querySelector('.hero > .hero-subtitle');
        
        // Clear will-change to free GPU resources
        if (logo) logo.style.willChange = 'auto';
        if (title) title.style.willChange = 'auto';
        if (subtitle) subtitle.style.willChange = 'auto';
        
        scrollEffectsEnabled = true;
        
        // Clear the timer if it exists
        if (animationCleanupTimer) {
            clearTimeout(animationCleanupTimer);
            animationCleanupTimer = null;
        }
    };
    
    // Auto-enable after animations complete (1.8s + 100ms buffer)
    if (hasHero) {
        animationCleanupTimer = setTimeout(enableScrollEffects, 1900);
    } else {
        scrollEffectsEnabled = true;
    }
    
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const scrolled = window.pageYOffset;
          
          // If user scrolls, immediately enable scroll effects and disable CSS animations
          if (scrolled > 0 && !scrollEffectsEnabled) {
            enableScrollEffects();
          }
          
          // Don't run effects if at top
          if (scrolled === 0) {
            ticking = false;
            return;
          }
          
          // Select elements dynamically
          const logo = document.querySelector('.hero > .logo-container'); 
          const title = document.querySelector('.hero > .hero-title');
          const subtitle = document.querySelector('.hero > .hero-subtitle');
          const content = document.querySelector('.content');
          
          // Check if we have a title to animate
          if (title) {
            
            // Disable CSS animations on first scroll
            if (!animationsDisabled) {
              if (logo) logo.style.animation = 'none';
              if (title) title.style.animation = 'none';
              if (subtitle) subtitle.style.animation = 'none';
              animationsDisabled = true;
            }

            // Parallax math
            const fadeVal = Math.max(0, 1 - (scrolled / 800));
            const blurVal = Math.max(Math.min(40, (scrolled / 30) - 5), 0);
            
            if (logo) {
              logo.style.transform = `translateY(${scrolled * 0.3}px)`;
              logo.style.opacity = fadeVal;
              logo.style.filter = `blur(${blurVal}px)`;
            }
            if (title) {
              title.style.transform = `translateY(${scrolled * 0.25}px)`;
              title.style.opacity = fadeVal;
              title.style.filter = `blur(${blurVal}px)`;
            }
            if (subtitle) {
              subtitle.style.transform = `translateY(${scrolled * 0.2}px)`;
              subtitle.style.opacity = fadeVal;
              subtitle.style.filter = `blur(${blurVal}px)`;
            }
          }
          
          // Content Reveal
          if (content && hasHero) {
            if (scrolled > 75) {
              content.classList.add('revealed');
            } else {
              content.classList.remove('revealed');
            }
          }
          
          ticking = false;
        });
        
        ticking = true;
      }
    });

// Function to determine the smaller margin
const getDynamicMargin = () => {
    const vh = window.innerHeight;
    const fivePercent = vh * 0.05;
    const thirtyPixels = 100;
    
    // "Which happens first" when scrolling up means the smaller pixel value
    const marginPx = Math.min(fivePercent, thirtyPixels);
    
    return `0px 0px -${marginPx}px 0px`;
};

const observerOptions = {
    threshold: 0.05,
    rootMargin: getDynamicMargin()
};
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        // Skip hero elements to prevent conflicts with CSS animations
        if (entry.target.closest('.hero')) return;
        
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        } else {
          // This resets the state when the element scrolls away
          entry.target.classList.remove('visible');
        }
      });
    }, observerOptions);

    // Observe all sections and feature cards (but not hero children)
    document.querySelectorAll('.section, .feature-card, .card').forEach(el => {
      observer.observe(el);
    });
    
    // Immediately show cards that are in viewport on page load (fixes mobile blog issue)
    // Delay slightly if hero exists to avoid conflicting with hero animations
    const cardRevealDelay = hasHero ? 1900 : 50;
    setTimeout(() => {
      document.querySelectorAll('.card').forEach(card => {
        const rect = card.getBoundingClientRect();
        const isInViewport = rect.top < window.innerHeight && rect.bottom > 0;
        // Also show immediately if no hero exists (blog posts)
        if (isInViewport || !hasHero) {
          card.classList.add('visible');
        }
      });
    }, cardRevealDelay);

    // Separate image observer with better settings
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        } else {
          entry.target.classList.remove('visible');
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    // Wait a moment for DOM to fully load, then observe images
    setTimeout(() => {
      const allImages = document.querySelectorAll('.content img, .card-image img');
      allImages.forEach(img => {
        imageObserver.observe(img);
      });
    }, 100);

    // Smooth card hover effects
    const cards = document.querySelectorAll('.card, .feature-card');
    
    cards.forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.transition = 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.transition = 'all 0.8s cubic-bezier(0.16, 1, 0.3, 1)';
      });
    });

    // Email Obfuscation
    const contactBtn = document.querySelector('.contact-button');
    if (contactBtn) {
        const user = "cory";
        const domain = "vitezengineering.com";
        const subject = "Inquiry via Vitez Engineering";
        
        contactBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = `mailto:${user}@${domain}?subject=${encodeURIComponent(subject)}`;
        });
    }

    // Blog pagination
    const currentPath = window.location.pathname;
    const currentIndex = blogPosts.findIndex(post => currentPath.endsWith(post.url));
    
    if (currentIndex !== -1) {
        const prev = blogPosts[currentIndex - 1];
        const next = blogPosts[currentIndex + 1];

        const navHTML = `
    <div class="blog-pagination">
        ${prev ? `
            <a href="${prev.url}" class="nav-arrow prev">
                &longleftarrow;
                <span>${prev.title}</span>
            </a>` : '<div></div>'}
            
        ${next ? `
            <a href="${next.url}" class="nav-arrow next">
                &longrightarrow;
                <span>${next.title}</span>
            </a>` : '<div></div>'}
    </div>
`;
        const card = document.querySelector('.card');
        if (card) {
            document.body.insertAdjacentHTML('beforeend', navHTML);
        }
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
