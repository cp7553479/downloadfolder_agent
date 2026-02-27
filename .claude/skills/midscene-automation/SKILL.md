---
name: Midscene Browser/Computer Automation
description: |
  Vision-driven browser/computer automation using Midscene. Operates entirely from screenshots — no DOM or accessibility labels required. Can interact with all visible elements on screen regardless of technology stack.

  Use this skill when the user wants to:
  - Browse, navigate, or open web pages
  - Scrape, extract, or collect data from websites
  - Fill out forms, click buttons, or interact with web elements
  - Verify, validate, or test frontend UI behavior
  - Take screenshots of web pages
  - Automate multi-step web workflows
  - Run browser automation or check website content
  - open app, press key, desktop, computer, click on screen, type text, screenshot desktop,
  launch application, switch window, desktop automation, control computer, mouse click, keyboard shortcut,
  screen capture, find on screen, read screen, verify window, close app, minimize window, maximize window

  Powered by Midscene.js (https://midscenejs.com)
allowed-tools:
  - Bash
---

# Browser Automation

> **CRITICAL RULES — VIOLATIONS WILL BREAK THE WORKFLOW:**
>
> 1. **Never run midscene commands in the background.** Each command must run synchronously so you can read its output (especially screenshots) before deciding the next action. Background execution breaks the screenshot-analyze-act loop.
> 2. **Run only one midscene command at a time.** Wait for the previous command to finish, read the screenshot, then decide the next action. Never chain multiple commands together.
> 3. **Allow enough time for each command to complete.** Midscene commands involve AI inference and screen interaction, which can take longer than typical shell commands. A typical command needs about 1 minute; complex `act` commands may need even longer.

Automate web browsing using `npx @midscene/web@1`. Launches a headless Chrome via Puppeteer that **persists across CLI calls** — no session loss between commands. Each CLI command maps directly to an MCP tool — you (the AI agent) act as the brain, deciding which actions to take based on the task target.

## When to Use

Use this skill when:
- The user wants to browse or navigate to a specific URL
- You need to scrape, extract, or collect data from websites
- You want to verify or test frontend UI behavior
- The user wants screenshots of web pages

If you need to preserve login sessions or work with the user's existing browser tabs, use the **Chrome Bridge Automation** skill instead. Read [chrome-bridge/SKILL.md](./chrome-bridge/SKILL.md) for Chrome Bridge Automation.


## Commands

### Connect to a Web Page

```bash
npx @midscene/web@1 connect --url https://example.com
```

Or just connect to the current page without specifying the URL:

```bash
npx @midscene/web@1 connect
```

When you continue the task, and the npx @midscene/web@1 close command is not executed, the browser will keep running in the background, so you can connect without the --url parameter.

### Take Screenshot

```bash
npx @midscene/web@1 take_screenshot
```

After taking a screenshot, read the saved image file to understand the current page state before deciding the next action.

### Perform Action

Use `act` to interact with the page and get the result. It autonomously handles all UI interactions internally — clicking, typing, scrolling, hovering, waiting, and navigating — so you should give it complex, high-level tasks as a whole rather than breaking them into small steps. Describe **what you want to do and the desired effect** in natural language:

```bash
# specific instructions
npx @midscene/web@1 act --prompt "open the website https://www.google.com"
npx @midscene/web@1 act --prompt "click the Login button and fill in the email field with 'user@example.com'"
npx @midscene/web@1 act --prompt "scroll down and click the Submit button"

# or target-driven instructions
npx @midscene/web@1 act --prompt "open the website https://www.google.com and Login with 'user@example.com'"

# The BEST PRACTICE instructions(detailed in a single act command)
npx @midscene/web@1 act --prompt "open the website https://www.google.com, then click the Login button and fill in the email field with 'user@example.com', then scroll down and click the Submit button"
```

### Disconnect

Disconnect from the page but keep the browser running:

```bash
npx @midscene/web@1 disconnect
```

### Close Browser

Close the browser completely when finished:

```bash
npx @midscene/web@1 close
```

## Workflow Pattern

The browser **persists across CLI calls** via a background Chrome process. Follow this pattern:

1. **Connect** to a URL to open a new tab
2. **Execute action** using `act` to perform the desired action or target-driven instructions.
3. **Close** the browser when all the tasks are done (or **disconnect** to keep it for later)

## Best Practices

1. **Always connect first**: Navigate to the target URL with `connect --url` before any interaction.
2. **Be specific about UI elements**: Instead of `"the button"`, say `"the blue Submit button in the contact form"`.
3. **Use natural language**: Describe what you see on the page, not CSS selectors. Say `"the red Buy Now button"` instead of `"#buy-btn"`.
4. **Handle loading states**: After navigation or actions that trigger page loads, take a screenshot to verify the page has loaded.
5. **Close when done**: Use `close` to shut down the browser and free resources.
6. **Never run in background**: Every midscene command must run synchronously — background execution breaks the screenshot-analyze-act loop.
7. **Batch related operations into a single `act` command**: When performing consecutive operations within the same page, combine them into one `act` prompt instead of splitting them into separate commands. For example, "fill in the email and password fields, then click the Login button" should be a single `act` call, not three. This reduces round-trips, avoids unnecessary screenshot-analyze cycles, and is significantly faster. Try to describe the operations in a single `act` command as much as possible, if you cannot determine the specific operations, you can describe the purpose in a single `act` command, let @midscene/web@1 analyze and execute the operations by itself.
8. **Summarize report files after completion**: After finishing the automation task, collect and summarize all report files (screenshots, logs, output files, etc.) for the user. Present a clear summary of what was accomplished, what files were generated, and where they are located, making it easy for the user to review the results.

**Example — Dropdown selection:**

```bash
npx @midscene/web@1 act --prompt "click the country dropdown and select Japan"
npx @midscene/web@1 take_screenshot
```

**Example — Form interaction:**

```bash
npx @midscene/web@1 act --prompt "fill in the email field with 'user@example.com' and the password field with 'pass123', then click the Log In button"
npx @midscene/web@1 take_screenshot
```

## Troubleshooting

### Miss MIDSCENE_MODEL_API_KEY
Midscene requires models with strong visual grounding capabilities. The following environment variables must be configured — either as system environment variables or in a `.env` file in the current working directory (Midscene loads `.env` automatically):

```bash
MIDSCENE_MODEL_API_KEY="your-api-key"
MIDSCENE_MODEL_NAME="model-name"
MIDSCENE_MODEL_BASE_URL="https://..."
MIDSCENE_MODEL_FAMILY="family-identifier"
```
MIDSCENE_MODEL_FAMILY: the family of the model, such as gemini, "qwen3-vl", "qwen2.5-vl", "doubao-vision","glm-v","auto-glm","auto-glm-multilingual","vlm-ui-tars-doubao-1.5". This parameter is used to adapt to the interfaces of different models.

Commonly used models: Doubao Seed 1.6, Qwen3-VL, Zhipu GLM-4.6V, Gemini-3-Pro, Gemini-3-Flash.

If the model is not configured, ask the user to set it up. See [Model Configuration](https://midscenejs.com/model-common-config) for supported providers.

### Connection Failures
- Ensure Chrome/Chromium is installed on the system (Puppeteer downloads its own by default).
- Check that no firewall blocks local Chrome debugging ports.

### API Key Errors
- Check `.env` file contains `MIDSCENE_MODEL_API_KEY=<your-key>`.
- Verify the key is valid for the configured model provider.

### Timeouts
- Web pages may take time to load. After connecting, take a screenshot to verify readiness before interacting.
- For slow pages, wait briefly between steps.

### Screenshots Not Displaying
- The screenshot path is an absolute path to a local file. Use the Read tool to view it.

# Computer Automation

Read [computer-automation/SKILL.md](./computer-automation/SKILL.md) for computer automation.