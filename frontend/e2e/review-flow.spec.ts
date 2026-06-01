import { test, expect } from '@playwright/test'

test('review queue approve and publish draft actions show feedback', async ({ page }) => {
  await page.route('**/content-items', async (route) => {
    const method = route.request().method()
    if (method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([{ id: '1', title: 'Item 1', status: 'ready_for_review' }]),
      })
      return
    }
    await route.continue()
  })

  await page.route('**/content-items/1/approve', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: '1', title: 'Item 1', status: 'approved' }),
    })
  })

  await page.route('**/content-items/1/publish-draft', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        content_item: { id: '1', title: 'Item 1', status: 'approved' },
        publication: { platform: 'wordpress', operation: 'create_draft', success: true },
      }),
    })
  })

  await page.route('**/content-items/1/request-changes', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: '1', title: 'Item 1', status: 'qa_failed' }),
    })
  })

  await page.route('**/connectors/diagnostics', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ connectors: [] }) })
  })

  await page.route('**/runs/telemetry/summary**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_runs: 1,
        successful_runs: 1,
        failed_runs: 0,
        total_estimated_cost_usd: 0.01,
        total_estimated_tokens: 100,
        by_run_type: { produce_content: 1 },
      }),
    })
  })

  await page.goto('/review-queue')

  await expect(page.getByRole('heading', { name: 'Review Queue' })).toBeVisible()
  await expect(page.getByText('Item 1')).toBeVisible()

  await page.getByRole('button', { name: 'Approve' }).click()
  await expect(page.getByText('Item approved.')).toBeVisible()

  await page.getByRole('button', { name: 'Publish Draft' }).click()
  await expect(page.getByText('Draft published.')).toBeVisible()
})
