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
    { url: "/blog-post/re.html", title: "Responsible Engineer" },
    { url: "/blog-post/torture.html", title: "Torturing Terrorist" },
    { url: "/blog-post/bike-commuting.html", title: "Bike Commuting" },
    { url: "/blog-post/10-precepts.html", title: "Ten Precepts" },
    { url: "/blog-post/happiness.html", title: "Happiness" },
    { url: "/blog-post/self-improvement.html", title: "Self Improvement" },
    { url: "/blog-post/humes-problem.html", title: "Hume's Problem" },
    { url: "/blog-post/gay-engineer.html", title: "Gay Engineer" },
    { url: "/blog-post/llm-in-engineering.html", title: "LLMs in Engineering" },
    { url: "/blog-post/listening.html", title: "Listening" }
];



window.addEventListener('DOMContentLoaded', () => {

    // Parallax effect on scroll
    let ticking = false;
    
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const scrolled = window.pageYOffset;
          
          // Parallax on hero elements
          const logo = document.querySelector('.logo-container');
          const title = document.querySelector('.hero-title');
          const subtitle = document.querySelector('.hero-subtitle');
          
          if (logo) logo.style.transform = `translateY(${scrolled * 0.4}px)`;
          if (title) title.style.transform = `translateY(${scrolled * 0.3}px)`;
          if (subtitle) subtitle.style.transform = `translateY(${scrolled * 0.2}px)`;
          
          ticking = false;
        });
        
        ticking = true;
      }
    });

    // Intersection Observer for scroll animations
    const observerOptions = {
      threshold: 0.15,
      rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, observerOptions);

    // Observe all sections and feature cards
    document.querySelectorAll('.section, .feature-card').forEach(el => {
      observer.observe(el);
    });

    // Smooth gradient animation on cards
    const cards = document.querySelectorAll('.card, .feature-card');
    
    cards.forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
      });
    });

    // Email Obfuscation
const contactBtn = document.querySelector('.contact-button');
if (contactBtn) {
    const user = "cory";
    const domain = "vitezengineering.com";
    const subject = "Inquiry via Vitez Engineering";
    
    // This pieces the email together dynamically
    contactBtn.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = `mailto:${user}@${domain}?subject=${encodeURIComponent(subject)}`;
    });
}

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


});
