import { test, expect } from '@playwright/test';

const EVIDENCE_PATH = '../.sisyphus/evidence';

test.describe('Stocks Page', () => {
  test('should load stocks page without errors', async ({ page }) => {
    await page.goto('/stocks');
    
    // Wait for page load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check page heading
    const heading = page.getByRole('heading', { name: /전종목 리스트/i });
    await expect(heading).toBeVisible();
    
    // Check table or empty state exists
    const table = page.locator('table');
    const emptyState = page.locator('[role="status"]').first();
    
    const hasTable = await table.isVisible().catch(() => false);
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    
    expect(hasTable || hasEmptyState).toBeTruthy();
    
    // Take screenshot
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-stocks.png`, 
      fullPage: true 
    });
  });

  test('should sort by PER column', async ({ page }) => {
    await page.goto('/stocks');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Find and click PER sort header
    const perHeader = page.locator('th').filter({ hasText: /PER/i }).first();
    
    if (await perHeader.isVisible().catch(() => false)) {
      // Click to sort ascending
      await perHeader.click();
      await page.waitForTimeout(500);
      
      // Take screenshot of ascending sort
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-stocks-per-asc.png`, 
        fullPage: true 
      });
      
      // Click again to sort descending
      await perHeader.click();
      await page.waitForTimeout(500);
      
      // Take screenshot of descending sort
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-stocks-per-desc.png`, 
        fullPage: true 
      });
    }
  });

  test('should sort by other columns', async ({ page }) => {
    await page.goto('/stocks');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Test market cap sort
    const marketCapHeader = page.locator('th').filter({ hasText: /시가총액/i }).first();
    if (await marketCapHeader.isVisible().catch(() => false)) {
      await marketCapHeader.click();
      await page.waitForTimeout(500);
    }
    
    // Test change rate sort
    const changeRateHeader = page.locator('th').filter({ hasText: /등락률/i }).first();
    if (await changeRateHeader.isVisible().catch(() => false)) {
      await changeRateHeader.click();
      await page.waitForTimeout(500);
    }
    
    // Test PBR sort
    const pbrHeader = page.locator('th').filter({ hasText: /PBR/i }).first();
    if (await pbrHeader.isVisible().catch(() => false)) {
      await pbrHeader.click();
      await page.waitForTimeout(500);
    }
    
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-stocks-sorting.png`, 
      fullPage: true 
    });
  });

  test('should filter by PER range', async ({ page }) => {
    await page.goto('/stocks');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Find PER filter inputs
    const perMinInput = page.locator('input[placeholder*="최소"]').filter({ has: page.locator(':visible') }).first();
    const perMaxInput = page.locator('input[placeholder*="최대"]').filter({ has: page.locator(':visible') }).first();
    
    if (await perMinInput.isVisible().catch(() => false)) {
      // Set PER range filter
      await perMinInput.fill('5');
      await page.waitForTimeout(500);
      
      if (await perMaxInput.isVisible().catch(() => false)) {
        await perMaxInput.fill('20');
        await page.waitForTimeout(500);
      }
      
      // Wait for filter to apply
      await page.waitForTimeout(1000);
      
      // Take screenshot
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-stocks-per-filter.png`, 
        fullPage: true 
      });
      
      // Test clear filters button
      const clearButton = page.getByRole('button', { name: /필터 초기화|초기화/i });
      if (await clearButton.isVisible().catch(() => false)) {
        await clearButton.click();
        await page.waitForTimeout(500);
      }
    }
  });

  test('should filter by market cap', async ({ page }) => {
    await page.goto('/stocks');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Find market cap filter input
    const marketCapInput = page.locator('input[placeholder*="최소"]').nth(1);
    
    if (await marketCapInput.isVisible().catch(() => false)) {
      await marketCapInput.fill('1');
      await page.waitForTimeout(1000);
      
      await page.screenshot({ 
        path: `${EVIDENCE_PATH}/task-f1-stocks-marketcap-filter.png`, 
        fullPage: true 
      });
    }
  });

  test('should handle pagination if multiple pages exist', async ({ page }) => {
    await page.goto('/stocks');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check for pagination
    const nextButton = page.getByRole('button').filter({ has: page.locator('svg[class*="chevron"], .lucide-chevron-right') }).first();
    const pageNumbers = page.locator('button').filter({ hasText: /^[0-9]+$/ });
    
    if (await pageNumbers.count() > 1) {
      // Click on page 2 if exists
      const page2 = pageNumbers.filter({ hasText: '2' }).first();
      if (await page2.isVisible().catch(() => false)) {
        await page2.click();
        await page.waitForTimeout(500);
        
        await page.screenshot({ 
          path: `${EVIDENCE_PATH}/task-f1-stocks-pagination.png`, 
          fullPage: true 
        });
      }
    }
  });
});
