# 🚀 Deployment Guide - Aniket Kumar Portfolio

This guide will help you deploy your portfolio website to Vercel with a custom domain.

## 🎯 Quick Start

### Option 1: Deploy via GitHub (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial portfolio website commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/portfolio-website.git
   git push -u origin main
   ```

2. **Deploy on Vercel**:
   - Visit [vercel.com](https://vercel.com)
   - Click "Sign up" and choose "Continue with GitHub"
   - Click "New Project"
   - Import your `portfolio-website` repository
   - Click "Deploy" (Vercel will automatically detect it's a static site)
   - Your site will be live in ~30 seconds! 🎉

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   # From the portfolio-website directory
   vercel
   
   # Follow the prompts:
   # ? Set up and deploy "portfolio-website"? Y
   # ? Which scope? (your-username)
   # ? Link to existing project? N
   # ? What's your project's name? aniket-kumar-portfolio
   # ? In which directory is your code located? ./
   ```

4. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

## 🌐 Custom Domain Setup (aniketkumar.dev)

### Step 1: Purchase Domain
- Buy `aniketkumar.dev` from a domain registrar like:
  - [Namecheap](https://www.namecheap.com)
  - [GoDaddy](https://www.godaddy.com)
  - [Cloudflare Registrar](https://www.cloudflare.com/products/registrar/)

### Step 2: Add Domain to Vercel
1. Go to your project dashboard on Vercel
2. Click "Settings" → "Domains"
3. Add `aniketkumar.dev` and `www.aniketkumar.dev`
4. Vercel will show DNS configuration requirements

### Step 3: Configure DNS
Add these records to your domain's DNS settings:

**For Root Domain (aniketkumar.dev):**
```
Type: A
Name: @
Value: 76.76.21.21
```

**For WWW Subdomain:**
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

### Step 4: Wait for Propagation
- DNS changes can take 5 minutes to 24 hours
- Check status at [whatsmydns.net](https://www.whatsmydns.net)
- Vercel will show a green checkmark when ready

## 📧 Contact Form Setup

Your contact form currently shows a success message. To make it functional:

### Option 1: Formspree (Free & Easy)
1. Sign up at [formspree.io](https://formspree.io)
2. Create a new form
3. Update your contact form:
   ```html
   <form class="contact-form" action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
   ```

### Option 2: Netlify Forms (If you switch to Netlify)
1. Add `netlify` attribute to your form:
   ```html
   <form class="contact-form" netlify>
   ```

### Option 3: Custom Backend
- Use services like EmailJS, SendGrid, or build your own API

## 🔄 Automatic Deployments

Once connected to GitHub:
- Every push to `main` branch automatically deploys to production
- Pull requests create preview deployments
- No manual deployment needed!

## 📊 Add Analytics (Optional)

### Google Analytics
1. Create account at [analytics.google.com](https://analytics.google.com)
2. Get your Measurement ID
3. Add to both HTML files:
   ```html
   <!-- Before closing </head> tag -->
   <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'GA_MEASUREMENT_ID');
   </script>
   ```

### Vercel Analytics
1. Enable in your Vercel dashboard
2. Add script to your HTML files:
   ```html
   <script src="/_vercel/insights/script.js" defer></script>
   ```

## ⚡ Performance Optimization

Your site is already optimized with:
- ✅ Responsive images
- ✅ Minified CSS/JS
- ✅ Lazy loading
- ✅ Efficient caching headers
- ✅ Modern web standards

## 🔧 Common Issues & Solutions

### Issue: "Domain not working"
- **Solution**: Check DNS propagation, wait 24 hours

### Issue: "Contact form not submitting"
- **Solution**: Set up Formspree or similar service

### Issue: "Images not loading"
- **Solution**: Check image URLs, ensure they're accessible

### Issue: "Mobile view broken"
- **Solution**: Website is responsive, clear browser cache

## 🎯 Next Steps After Deployment

1. **Test Everything**: Check all links, forms, and responsiveness
2. **SEO Optimization**: 
   - Submit to Google Search Console
   - Create sitemap.xml
   - Optimize meta descriptions
3. **Content Updates**: 
   - Add real project screenshots
   - Update social media links
   - Add your actual resume/CV
4. **Performance Monitoring**: 
   - Set up analytics
   - Monitor Core Web Vitals
   - Regular performance audits

## 📞 Support

If you need help with deployment:
- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Discord**: [Vercel Community](https://discord.gg/vercel)
- **Contact**: contact@aniketkumar.dev

---

🎉 **Congratulations!** Your portfolio is now live at `https://yourusername.vercel.app` and soon at `https://aniketkumar.dev`!
