import { test, expect } from '@playwright/test'

test('review queue shows failure feedback when publish draft is blocked by approval gate', async ({ page }) => {
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

  await page.route('**/content-items/1/publish-draft', async (route) => {
    await route.fulfill({
      status: 400,
      contentType: 'application/json',
      body: JSON.stringify({
        detail: 'Content item must be approved before draft publish.',
      }),
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
        budget_limited_runs: 0,
        budget_exceeded_runs: 0,
        by_run_type: { produce_content: 1 },
      }),
    })
  })

  await page.goto('/review-queue')

  await expect(page.getByRole('heading', { name: 'Review Queue' })).toBeVisible()
  await page.getByRole('button', { name: 'Publish Draft' }).click()
  await expect(page.getByText('Action failed. Please try again.')).toBeVisible()
})
