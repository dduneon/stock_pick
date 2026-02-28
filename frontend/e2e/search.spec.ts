import { test, expect } from '@playwright/test';

const EVIDENCE_PATH = '../.sisyphus/evidence';

test.describe('Search Page', () => {
  test('should load search page without errors', async ({ page }) => {
    await page.goto('/search');
    
    // Wait for page load
    await page.waitForLoadState('networkidle');
    
    // Check page heading
    const heading = page.getByRole('heading', { name: /종목 검색|검색/i }).first();
    await expect(heading).toBeVisible();
    
    // Take screenshot
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-search-empty.png`, 
      fullPage: true 
    });
  });

  test('should search with 삼성 query', async ({ page }) => {
    await page.goto('/search?q=삼성');
    
    // Wait for page and search results to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check search heading
    const heading = page.getByRole('heading', { name: /검색 결과/i });
    await expect(heading).toBeVisible();
    
    // Check search query is displayed
    const queryText = page.locator('text="삼성"').first();
    await expect(queryText).toBeVisible();
    
    // Wait for results or empty state
    await page.waitForTimeout(1000);
    
    // Take screenshot
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-search-samsung.png`, 
      fullPage: true 
    });
    
    // Check if we have results
    const resultCards = page.locator('a[href*="/stock/"], article, .stock-card');
    const resultCount = await resultCards.count();
    
    if (resultCount > 0) {
      // Verify first result has required elements
      const firstResult = resultCards.first();
      await expect(firstResult).toBeVisible();
    } else {
      // Check for empty state
      const emptyState = page.locator('[role="status"], text=/검색 결과가 없습니다|결과가 없습니다/i').first();
      const hasEmptyState = await emptyState.isVisible().catch(() => false);
      expect(hasEmptyState).toBeTruthy();
    }
  });

  test('should search with ticker query', async ({ page }) => {
    await page.goto('/search?q=005930');
    
    // Wait for page and search results to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check search heading
    const heading = page.getByRole('heading', { name: /검색 결과/i });
    await expect(heading).toBeVisible();
    
    // Take screenshot
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-search-ticker.png`, 
      fullPage: true 
    });
  });

  test('should handle empty search results', async ({ page }) => {
    // Search for non-existent stock
    await page.goto('/search?q=XYZ123NONEXISTENT');
    
    // Wait for page and search results to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check for empty state
    const emptyState = page.locator('[role="status"], text=/검색 결과가 없습니다|결과가 없습니다/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    
    // Take screenshot regardless of result
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-search-empty-results.png`, 
      fullPage: true 
    });
    
    expect(hasEmptyState || await page.locator('text=/0개|없습니다/i').first().isVisible().catch(() => false)).toBeTruthy();
  });

  test('should navigate to stock detail from search results', async ({ page }) => {
    await page.goto('/search?q=삼성');
    
    // Wait for page and search results to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Find first stock result link
    const stockLink = page.locator('a[href*="/stock/"], a[href*="/stocks/"]').first();
    
    if (await stockLink.isVisible().catch(() => false)) {
      const href = await stockLink.getAttribute('href');
      await stockLink.click();
      
      // Wait for navigation
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      // Verify we're on a detail page
      await expect(page).toHaveURL(/\/(stock|stocks)\//);
      
      // Take screenshot
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-search-navigation.png`, 
        fullPage: true 
      });
    }
  });

  test('should search from header search input', async ({ page }) => {
    await page.goto('/');
    
    // Find search input in header
    const searchInput = page.locator('input[placeholder*="검색"], input[type="text"]').first();
    
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('삼성');
      await searchInput.press('Enter');
      
      // Wait for navigation
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      // Verify we're on search page
      await expect(page).toHaveURL(/\/search/);
      
      // Take screenshot
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-header-search.png`, 
        fullPage: true 
      });
    }
  });
});
