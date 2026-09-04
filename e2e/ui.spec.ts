import { test, expect } from '@playwright/test';

test.describe('SatQuery AI UI E2E Regression', () => {

  let consoleErrors: string[] = [];

  test.beforeEach(({ page }) => {
    consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        const text = msg.text();
        if (
          !text.includes('favicon.ico') && 
          !text.includes('Failed to load resource: net::ERR_CONNECTION_REFUSED') &&
          !text.includes('status of 400') 
        ) {
          consoleErrors.push(text);
        }
      }
    });
    page.on('pageerror', err => {
      consoleErrors.push(err.message);
    });
  });

  test.afterEach(() => {
    expect(consoleErrors).toEqual([]);
  });

  test('1. APPLICATION STARTUP / LANDING', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('LAUNCH SATQUERY AI')).toBeVisible();
    await page.getByText('LAUNCH SATQUERY AI').click();
    await expect(page).toHaveURL(/.*#\/workspace/);

    await expect(page.locator('aside').getByText('AI WORKSPACE')).toBeVisible();
    await expect(page.locator('aside').getByText('SINGLE IMAGE')).toBeVisible();
    await expect(page.locator('aside').getByText('CHANGE DETECTION')).toBeVisible();
    await expect(page.locator('aside').getByText('OPTICAL + SAR')).toBeVisible();
  });

  test('2. SINGLE IMAGE — VQA', async ({ page }) => {
    await page.goto('/#/single-image');
    
    await page.getByText('Synthetic Urban Growth Corridors').click();
    await page.getByText('VISUAL QUESTION ANSWERING').click();

    const textarea = page.locator('textarea').first();
    await textarea.fill('What are the major land-cover features visible in this image?');

    const analyzePromise = page.waitForResponse(response => 
      response.url().includes('/analyze') && response.request().method() === 'POST'
    );

    await page.getByText('TRANSMIT VQA QUERY').click();

    const response = await analyzePromise;
    expect(response.status()).toBe(200);

    await expect(page.getByTestId('task-badge')).toHaveText('Visual Question Answering', { timeout: 15000 });
    await expect(page.getByText('Execution Trace')).toBeVisible();
    await expect(page.getByText('CONFIDENCE:')).toBeVisible();
  });

  test('3. SINGLE IMAGE — SCENE DESCRIPTION', async ({ page }) => {
    await page.goto('/#/single-image');
    await page.getByText('Synthetic Urban Growth Corridors').click();

    await page.getByText('SCENE DESCRIPTION').click();
    
    const analyzePromise = page.waitForResponse(response => 
      response.url().includes('/analyze') && response.request().method() === 'POST'
    );
    
    await page.getByText('GENERATE SCENE DESCRIPTION').click();
    const response = await analyzePromise;
    expect(response.status()).toBe(200);

    await expect(page.getByTestId('task-badge')).toHaveText('Scene Captioning', { timeout: 15000 });
  });

  test('4. SINGLE IMAGE — GROUNDING', async ({ page }) => {
    await page.goto('/#/single-image');
    await page.getByText('Synthetic Urban Growth Corridors').click();

    await page.getByText('REGION GROUNDING').click();

    const input = page.locator('input[type="text"]').first();
    await input.fill('Highlight the major built-up areas.');

    const analyzePromise = page.waitForResponse(response => 
      response.url().includes('/analyze') && response.request().method() === 'POST'
    );
    
    await page.getByText('EXTRACT BOUNDING COORDINATES').click();
    const response = await analyzePromise;
    expect(response.status()).toBe(200);

    await expect(page.getByTestId('task-badge')).toHaveText('Region Grounding', { timeout: 15000 });
  });

  test('5. CHANGE DETECTION / TEMPORAL', async ({ page }) => {
    await page.goto('/#/change-detection');
    await page.getByText('LOAD SYNTHETIC FLOOD MONITORING PAIR').click();

    const analyzePromise = page.waitForResponse(response => 
      response.url().includes('/analyze') && response.request().method() === 'POST'
    );

    await page.getByText('EXECUTE CHANGE DETECTION').click();
    const response = await analyzePromise;
    expect(response.status()).toBe(200);

    await expect(page.getByTestId('task-badge')).toHaveText('Temporal Change Description', { timeout: 15000 });
  });

  test('6. OPTICAL + SAR', async ({ page }) => {
    await page.goto('/#/optical-sar');
    await page.getByText('LOAD SYNTHETIC OPTICAL/SAR PAIR').click();

    const analyzePromise = page.waitForResponse(response => 
      response.url().includes('/analyze') && response.request().method() === 'POST'
    );

    await page.getByText('EXECUTE OPTICAL + SAR FUSION').click();
    const response = await analyzePromise;
    expect(response.status()).toBe(200);

    await expect(page.getByTestId('task-badge')).toHaveText('CROMA Multimodal Classifier', { timeout: 15000 });
  });

  test('7. WORKFLOW STATE ISOLATION', async ({ page }) => {
    await page.goto('/#/optical-sar');
    await page.getByText('LOAD SYNTHETIC OPTICAL/SAR PAIR').click();
    await page.getByText('EXECUTE OPTICAL + SAR FUSION').click();
    await expect(page.getByTestId('task-badge')).toHaveText('CROMA Multimodal Classifier', { timeout: 15000 });

    await page.goto('/#/single-image');
    await page.getByText('Synthetic Urban Growth Corridors').click();
    await page.getByText('VISUAL QUESTION ANSWERING').click();
    
    await expect(page.getByTestId('task-badge')).not.toBeVisible();

    await page.getByText('TRANSMIT VQA QUERY').click();
    await expect(page.getByTestId('task-badge')).toHaveText('Visual Question Answering', { timeout: 15000 });

    await page.getByText('SCENE DESCRIPTION').click();
    await page.getByText('GENERATE SCENE DESCRIPTION').click();
    await expect(page.getByTestId('task-badge')).toHaveText('Scene Captioning', { timeout: 15000 });
  });

  test('8. INVALID INPUT / ERROR HANDLING & 9. RECOVERY', async ({ page }) => {
    await page.goto('/#/workspace');
    
    const fileInput = page.locator('input[type="file"]').first();
    await fileInput.setInputFiles({
      name: 'corrupt.tif',
      mimeType: 'image/tiff',
      buffer: Buffer.from('this is not a valid tiff file')
    });

    await page.goto('/#/single-image');
    page.on('dialog', dialog => dialog.accept());
    await page.getByText('VISUAL QUESTION ANSWERING').click();
    await page.getByText('TRANSMIT VQA QUERY').click();

    await page.getByText('Synthetic Urban Growth Corridors').click();
    await page.getByText('TRANSMIT VQA QUERY').click();
    await expect(page.getByTestId('task-badge')).toHaveText('Visual Question Answering', { timeout: 15000 });
  });

});
