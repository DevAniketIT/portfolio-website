# Aniket Kumar - Portfolio Website

A modern, responsive portfolio website showcasing projects, skills, and professional experience.

## 🚀 Features

- **Responsive Design**: Optimized for all devices (desktop, tablet, mobile)
- **Modern UI/UX**: Clean, professional design with smooth animations
- **Project Showcase**: Interactive project gallery with filtering capabilities
- **Contact Form**: Functional contact form with validation
- **Performance Optimized**: Fast loading with optimized images and code
- **SEO Friendly**: Semantic HTML and meta tags for better search visibility
- **Cross-Browser Compatible**: Works across all modern browsers

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with CSS Grid and Flexbox
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Inter)
- **Deployment**: Vercel

## 📁 Project Structure

```
portfolio-website/
├── index.html          # Main landing page
├── projects.html       # Projects showcase page
├── style.css          # All styling and responsive design
├── script.js          # Interactive functionality
├── README.md          # Project documentation
└── vercel.json        # Vercel deployment configuration
```

## 🎨 Sections

### Landing Page (index.html)
- **Hero Section**: Introduction with call-to-action buttons
- **About Section**: Personal background and statistics
- **Skills Section**: Technical skills organized by category
- **Contact Section**: Contact information and form

### Projects Page (projects.html)
- **Project Grid**: Interactive showcase of projects
- **Filtering**: Filter projects by category (Web Apps, APIs, Mobile)
- **Project Details**: Live demos, GitHub links, and tech stacks
- **Statistics**: Project metrics and achievements

## 🚀 Getting Started

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/portfolio-website.git
cd portfolio-website
```

2. Open `index.html` in your browser or use a local server:
```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx http-server

# Using Live Server (VS Code extension)
# Right-click index.html and select "Open with Live Server"
```

3. Visit `http://localhost:8000` in your browser

### Deployment to Vercel

1. **Option 1: Deploy via GitHub**
   - Push your code to a GitHub repository
   - Visit [vercel.com](https://vercel.com)
   - Sign in with GitHub
   - Click "New Project" and import your repository
   - Configure project settings (already set in vercel.json)
   - Deploy!

2. **Option 2: Deploy via Vercel CLI**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Deploy to production
vercel --prod
```

3. **Custom Domain Setup**
   - In Vercel dashboard, go to your project settings
   - Navigate to "Domains" section
   - Add your custom domain (e.g., aniketkumar.dev)
   - Follow DNS configuration instructions

## 📱 Responsive Breakpoints

- **Desktop**: 1200px and above
- **Tablet**: 768px - 1199px
- **Mobile**: 480px - 767px
- **Small Mobile**: Below 480px

## 🎯 Performance Features

- Lazy loading for images
- CSS animations with GPU acceleration
- Optimized font loading
- Minified and compressed assets
- Intersection Observer for scroll animations
- Service Worker ready (PWA capabilities)

## 📧 Contact Form Integration

The contact form is currently set up for client-side validation. To make it functional:

1. **Using Formspree**:
   - Sign up at [formspree.io](https://formspree.io)
   - Replace form action with your Formspree endpoint
   - Update form method to POST

2. **Using Netlify Forms**:
   - Add `netlify` attribute to the form element
   - Deploy to Netlify
   - Forms will be automatically handled

3. **Custom Backend**:
   - Integrate with your preferred backend service
   - Update the form submission handling in script.js

## 🔧 Customization

### Colors and Branding
Update CSS variables in `style.css`:
```css
:root {
    --primary-color: #3b82f6;
    --secondary-color: #1e293b;
    --accent-color: #f59e0b;
    /* Add your brand colors */
}
```

### Content Updates
1. **Personal Information**: Update name, title, and bio in HTML files
2. **Projects**: Replace project data in `projects.html`
3. **Skills**: Modify skill categories in the skills section
4. **Social Links**: Update social media links throughout the site
5. **Contact Info**: Update email and social links

### Adding New Sections
1. Add HTML structure to `index.html`
2. Create corresponding CSS styles in `style.css`
3. Add any interactive functionality to `script.js`

## 📊 Analytics

To add analytics tracking:

1. **Google Analytics**:
```html
<!-- Add to <head> of both HTML files -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

2. **Vercel Analytics**:
   - Enable in Vercel dashboard
   - Add analytics script to HTML files

## 🌟 Features to Add

- [ ] Blog section
- [ ] Dark/Light mode toggle
- [ ] Multi-language support
- [ ] PWA functionality
- [ ] Advanced animations (GSAP)
- [ ] CMS integration
- [ ] E-commerce integration
- [ ] Advanced SEO optimizations

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/portfolio-website/issues).

## 📞 Support

If you have any questions or need help with deployment:

- **Email**: contact@aniketkumar.dev
- **LinkedIn**: [linkedin.com/in/aniketkumar](https://linkedin.com/in/aniketkumar)
- **GitHub**: [github.com/aniketkumar](https://github.com/aniketkumar)

---

**Built with ❤️ by Aniket Kumar**
