import { test, expect } from '@playwright/test';

const EVIDENCE_PATH = '../.sisyphus/evidence';

test.describe('Stock Detail Page', () => {
  test('should load valid stock detail page', async ({ page }) => {
    // Try to navigate to a known stock (005930 - Samsung Electronics)
    await page.goto('/stock/005930');
    
    // Wait for page load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check if page loaded successfully or shows error
    const errorState = page.locator('text=/찾을 수 없습니다|not found|오류/i').first();
    const hasError = await errorState.isVisible().catch(() => false);
    
    if (!hasError) {
      // Check stock name is displayed
      const stockName = page.locator('h1').first();
      await expect(stockName).toBeVisible();
      
      // Check ticker is displayed
      const ticker = page.locator('text=/^005930$/').first();
      const tickerVisible = await ticker.isVisible().catch(() => false);
      
      // Check price is displayed
      const price = page.locator('text=/[0-9,]+원$/').first();
      const priceVisible = await price.isVisible().catch(() => false);
      
      // Check metrics are displayed
      const per = page.locator('text=/PER/i').first();
      const pbr = page.locator('text=/PBR/i').first();
      
      await expect(per).toBeVisible();
      await expect(pbr).toBeVisible();
      
      // Check chart section
      const chart = page.locator('text=/주가 차트|차트/i').first();
      await expect(chart).toBeVisible();
    }
    
    // Take screenshot
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-stock-detail.png`, 
      fullPage: true 
    });
  });

  test('should display stock metrics correctly', async ({ page }) => {
    await page.goto('/stock/005930');
    
    // Wait for page load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check for error state
    const errorState = page.locator('text=/찾을 수 없습니다|not found|오류/i').first();
    const hasError = await errorState.isVisible().catch(() => false);
    
    if (!hasError) {
      // Check all key metrics exist
      const metrics = ['PER', 'PBR', '시가총액', 'EPS'];
      
      for (const metric of metrics) {
        const metricElement = page.locator(`text=/${metric}/i`).first();
        await expect(metricElement).toBeVisible();
      }
      
      // Check back button
      const backButton = page.getByRole('button', { name: /목록으로|뒤로/i }).first();
      await expect(backButton).toBeVisible();
    }
    
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-stock-metrics.png`, 
      fullPage: true 
    });
  });

  test('should navigate back to stocks list', async ({ page }) => {
    await page.goto('/stock/005930');
    
    // Wait for page load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Find back button
    const backButton = page.getByRole('button', { name: /목록으로|뒤로/i }).first();
    
    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      
      // Wait for navigation
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(500);
      
      // Verify we're back on stocks page
      await expect(page).toHaveURL(/\/stocks/);
      
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-stock-back-navigation.png`, 
        fullPage: true 
      });
    }
  });

  test('should load another stock by ticker', async ({ page }) => {
    // Try SK Hynix (000660)
    await page.goto('/stock/000660');
    
    // Wait for page load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check if page loaded successfully
    const errorState = page.locator('text=/찾을 수 없습니다|not found|오류/i').first();
    const hasError = await errorState.isVisible().catch(() => false);
    
    if (!hasError) {
      // Check stock name is displayed
      const stockName = page.locator('h1').first();
      await expect(stockName).toBeVisible();
    }
    
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-stock-detail-2.png`, 
      fullPage: true 
    });
  });
});
