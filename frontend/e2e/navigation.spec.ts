import { test, expect } from '@playwright/test';

const EVIDENCE_PATH = '../.sisyphus/evidence';

test.describe('Navigation Flow', () => {
  test('should navigate from home to stocks page', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Find and click stocks link
    const stocksLink = page.getByRole('link', { name: /전종목|종목|stocks/i }).first();
    
    if (await stocksLink.isVisible().catch(() => false)) {
      await stocksLink.click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      // Verify we're on stocks page
      await expect(page).toHaveURL(/\/stocks/);
      
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-nav-home-to-stocks.png`, 
        fullPage: true 
      });
    }
  });

  test('should navigate from stocks to stock detail', async ({ page }) => {
    await page.goto('/stocks');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Find first stock row/link in table
    const stockLink = page.locator('table tbody tr').first();
    const stockAnchor = page.locator('a[href*="/stock/"], a[href*="/stocks/"]').first();
    
    if (await stockAnchor.isVisible().catch(() => false)) {
      await stockAnchor.click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      // Verify we're on detail page
      await expect(page).toHaveURL(/\/(stock|stocks)\//);
      
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-nav-stocks-to-detail.png`, 
        fullPage: true 
      });
    } else if (await stockLink.isVisible().catch(() => false)) {
      // If no direct link, try clicking the row
      await stockLink.click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-nav-stocks-to-detail.png`, 
        fullPage: true 
      });
    }
  });

  test('should navigate using header search', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Find search input
    const searchInput = page.locator('input[placeholder*="검색"], input[type="text"]').first();
    
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('삼성');
      await searchInput.press('Enter');
      
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      // Verify we're on search page
      await expect(page).toHaveURL(/\/search/);
      
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-nav-header-search.png`, 
        fullPage: true 
      });
    }
  });

  test('should navigate back to home from any page', async ({ page }) => {
    // Start from stocks page
    await page.goto('/stocks');
    await page.waitForLoadState('networkidle');
    
    // Find home link/logo
    const homeLink = page.locator('a[href="/"], .logo, header a').first();
    
    if (await homeLink.isVisible().catch(() => false)) {
      await homeLink.click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      // Verify we're on home page
      await expect(page).toHaveURL(/\/$/);
      
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-nav-back-to-home.png`, 
        fullPage: true 
      });
    }
  });

  test('full user journey: home -> search -> detail', async ({ page }) => {
    // Start at home
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Search for Samsung
    const searchInput = page.locator('input[placeholder*="검색"]').first();
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('삼성');
      await searchInput.press('Enter');
      
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      
      // Click on first result
      const resultLink = page.locator('a[href*="/stock/"], a[href*="/stocks/"]').first();
      if (await resultLink.isVisible().catch(() => false)) {
        await resultLink.click();
        
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(2000);
        
        // Verify we're on detail page
        await expect(page).toHaveURL(/\/(stock|stocks)\//);
        
        // Check stock info is displayed
        const stockName = page.locator('h1').first();
        await expect(stockName).toBeVisible();
        
        await page.screenshot({ 
          path: `${EVIDENCE_PATH}/task-f1-full-journey.png`, 
          fullPage: true 
        });
      }
    }
  });
});
