# Weekly Notion cover rotation

This workflow updates a Notion page cover every **Sunday at 9:17 AM America/New_York**. It rotates through images alphabetically by filename (use `01.jpg`, `02.jpg`, and so on), then repeats. This uses no database or state file: the image is selected by the number of weeks since November 22, 2026. Manual runs during the same week choose the same image.

## Setup

1. **Prepare images.** Put `.jpg`, `.jpeg`, `.png`, `.gif`, or `.webp` images in `covers/`. Name them `01.jpg`, `02.jpg`, etc. Images should be appropriate dimensions for a wide Notion banner and reasonably small (e.g. under 5 MB each). At least one image is required.
2. **Create a public GitHub repository.** Go to https://github.com/new, choose **Public**, and name it `notion-weekly-cover`. GitHub hosts the image URLs; the images will be public, so do not use private or sensitive photos. Make sure the default branch is named **main**. Upload the *contents* of this folder to the repository root, including the hidden `.github/workflows/weekly-cover.yml` file. The GitHub web uploader can hide dotfolders on your computer; ensure this workflow file is actually present in the GitHub repository. A simple reliable upload method is Git from the terminal:

   ```bash
   cd path/to/notion-weekly-cover
   git init
   git add .
   git commit -m "Add weekly Notion cover rotation"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/notion-weekly-cover.git
   git push -u origin main
   ```

   If your new GitHub repository was initialized with a README, use a blank repository or reconcile its first commit before pushing.
3. **Create a Notion integration.** Visit https://www.notion.so/profile/integrations (or https://www.notion.so/my-integrations) and create an internal integration for the workspace containing the page. Enable **Update content** capability. Copy the integration secret. In the target Notion page, use `•••` → **Connections** → **Connect to** and select your integration, granting it access to the page.
4. **Get the page ID.** Open the Notion page in your browser and copy its URL. The page ID is the 32-character hexadecimal identifier near the end, sometimes followed by a `?` query string. Keep the ID only, not the whole URL (hyphens are also accepted).
5. **Add GitHub credentials and page ID.** In your GitHub repo: **Settings → Secrets and variables → Actions**. Under **Secrets**, create a repository secret `NOTION_TOKEN` with your integration secret. Under **Variables**, create a repository variable `NOTION_PAGE_ID` with the page ID. Do not put the token in a file or commit it.
6. **Test.** In the GitHub repo, open **Actions → Rotate Notion cover weekly → Run workflow → Run workflow**. Check that the run is green, and refresh your Notion page. A manual run before November 22, 2026 uses image 1. If the run fails, expand the 'Rotate Notion cover' step and read the error details. Verify the repo is public and images actually appear at `https://raw.githubusercontent.com/YOUR_USERNAME/notion-weekly-cover/main/covers/01.jpg` (substitute your actual name and extension).

## Maintenance and behavior

- Every Sunday starting **November 22, 2026**, the workflow uses image 1, image 2 the next Sunday, etc., wrapping to image 1 after the last image.
- Scheduled runs can be delayed or occasionally skipped by GitHub. The script computes the correct image for the week, so if a run is skipped, the next run catches up to the week's intended image. If desired, use **Run workflow** manually to retry.
- Adding/removing/renaming images will change the alphabetical sequence; the week index stays the same. For consistent cycling, keep the image set stable or reset `START_SUNDAY` in `rotate_cover.py` when changing the collection.
- This intentionally assumes your GitHub repo default branch is `main`; if not, adjust the URL segment in `rotate_cover.py` and the workflow location.
- The repository and its images must remain publicly readable. The integration token stays private in a GitHub Actions secret. Anyone with the public image URLs can view the photos.
- If you want a different day or hour, change `cron` in `.github/workflows/weekly-cover.yml`, while keeping `timezone: 'America/New_York'`. For the weekly schedule, prefer a minute other than `00`.
- **GitHub inactivity:** GitHub may disable scheduled workflows in public repos after 60 days without repository activity; if that happens, enable it again on the Actions page. Consider making a small repository update at least every couple of months, or use an alternative scheduler for permanently hands-off operation.

## References

- Notion page update API: https://developers.notion.com/reference/patch-page
- Notion integrations: https://www.notion.com/help/create-integrations-with-the-notion-api
- GitHub Actions schedules: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
