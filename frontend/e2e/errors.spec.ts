import { test, expect } from '@playwright/test';

const EVIDENCE_PATH = '../.sisyphus/evidence';

test.describe('Error Scenarios', () => {
  test('should show 404 page for invalid stock ticker', async ({ page }) => {
    // Navigate to non-existent stock
    await page.goto('/stock/INVALID999');
    
    // Wait for page load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check for error state - either 404 or error message
    const errorIndicators = [
      page.locator('text=/404|찾을 수 없습니다|not found|없습니다/i').first(),
      page.locator('[role="status"]').first(),
      page.locator('.error, .empty-state, [class*="error"]').first()
    ];
    
    let hasErrorIndicator = false;
    for (const indicator of errorIndicators) {
      const visible = await indicator.isVisible().catch(() => false);
      if (visible) {
        hasErrorIndicator = true;
        break;
      }
    }
    
    // Also check URL still shows the invalid ticker (not redirected)
    const url = page.url();
    expect(url).toContain('INVALID999');
    
    // Take screenshot of error state
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-error-404-stock.png`, 
      fullPage: true 
    });
    
    // Verify error message is shown
    expect(hasErrorIndicator).toBeTruthy();
  });

  test('should handle invalid ticker format gracefully', async ({ page }) => {
    // Test with various invalid formats
    const invalidTickers = ['ABC', '999999999', 'TEST!@#'];
    
    for (const ticker of invalidTickers) {
      await page.goto(`/stock/${ticker}`);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      // Page should not crash - check for error state or normal content
      const errorState = page.locator('text=/찾을 수 없습니다|오류|not found/i').first();
      const normalContent = page.locator('h1').first();
      
      const hasError = await errorState.isVisible().catch(() => false);
      const hasContent = await normalContent.isVisible().catch(() => false);
      
      expect(hasError || hasContent).toBeTruthy();
    }
    
    // Take screenshot of last error state
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-error-invalid-ticker.png`, 
      fullPage: true 
    });
  });

  test('should handle empty search gracefully', async ({ page }) => {
    await page.goto('/search?q=');
    
    // Wait for page load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    // Page should load without errors
    const heading = page.getByRole('heading').first();
    await expect(heading).toBeVisible();
    
    // Should show empty state or initial state
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-error-empty-search.png`, 
      fullPage: true 
    });
  });

  test('should provide navigation options on error pages', async ({ page }) => {
    await page.goto('/stock/NONEXISTENT');
    
    // Wait for page load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Look for navigation buttons
    const navigationButtons = [
      page.getByRole('button', { name: /목록으로|홈으로|돌아가기|이동/i }),
      page.locator('a').filter({ hasText: /목록|홈|돌아가기/i }),
      page.getByRole('link', { name: /전종목|홈|리스트/i })
    ];
    
    // At least one navigation option should exist
    let hasNavigation = false;
    for (const nav of navigationButtons) {
      const count = await nav.count();
      if (count > 0) {
        const visible = await nav.first().isVisible().catch(() => false);
        if (visible) {
          hasNavigation = true;
          break;
        }
      }
    }
    
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-error-navigation.png`, 
      fullPage: true 
    });
    
    // Navigation option should be available
    expect(hasNavigation).toBeTruthy();
  });

  test('should handle special characters in search', async ({ page }) => {
    const specialQueries = ['<script>', '"quotes"', 'test\'or\'1=1', '한글테스트'];
    
    for (const query of specialQueries) {
      await page.goto(`/search?q=${encodeURIComponent(query)}`);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      // Page should not crash
      const heading = page.getByRole('heading').first();
      const visible = await heading.isVisible().catch(() => false);
      expect(visible).toBeTruthy();
    }
    
    await page.screenshot({ 
      path: `${EVIDENCE_PATH}/task-f1-error-special-chars.png`, 
      fullPage: true 
    });
  });
});
