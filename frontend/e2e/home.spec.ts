import { test, expect } from '@playwright/test';

const EVIDENCE_PATH = '../.sisyphus/evidence';

test.describe('Home Page', () => {
  test('should load homepage without errors', async ({ page }) => {
    await page.goto('/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check page title
    await expect(page).toHaveTitle(/stock|recommendation/i);
    
    // Check main heading exists
    const heading = page.getByRole('heading', { name: /오늘의 추천 종목|추천/i });
    await expect(heading).toBeVisible();
    
    // Check header is visible
    const header = page.locator('header').first();
    await expect(header).toBeVisible();
    
    // Take screenshot
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-home.png`, 
      fullPage: true 
    });
  });

  test('should display stock recommendations', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait for content to load (either stock cards or empty state)
    await page.waitForTimeout(2000);
    
    // Check if we have stock cards or empty state
    const stockCards = page.locator('article');
    const emptyState = page.locator('[role="status"]').first();
    
    // Either stock cards or empty state should be visible
    const hasStockCards = await stockCards.count() > 0;
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    
    expect(hasStockCards || hasEmptyState).toBeTruthy();
    
    if (hasStockCards) {
      // Check first stock card has required elements
      const firstCard = stockCards.first();
      await expect(firstCard.locator('text=/^[0-9]{6}$/')).toBeVisible(); // Ticker pattern
      await expect(firstCard.locator('text=/원$/')).toBeVisible(); // Price with KRW
    }
    
    // Take screenshot
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-home-recommendations.png`, 
      fullPage: true 
    });
  });

  test('should have working navigation links', async ({ page }) => {
    await page.goto('/');
    
    // Check navigation to stocks page
    const stocksLink = page.getByRole('link', { name: /전종목|종목/i }).first();
    if (await stocksLink.isVisible().catch(() => false)) {
      await stocksLink.click();
      await expect(page).toHaveURL(/\/stocks/);
      await page.goBack();
    }
    
    // Check search input exists
    await page.goto('/');
    const searchInput = page.locator('input[placeholder*="검색"]').first();
    await expect(searchInput).toBeVisible();
  });

  test('should display disclaimer footer', async ({ page }) => {
    await page.goto('/');
    
    // Check disclaimer is visible
    const disclaimer = page.locator('text=/투자 고지|참고용/i').first();
    await expect(disclaimer).toBeVisible();
  });
});
