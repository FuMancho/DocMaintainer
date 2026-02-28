/**
 * DocMaintainer — Automated Weekly Research via Gemini API
 *
 * This Google Apps Script runs on a weekly schedule (free, no extra cost).
 * It calls the Gemini API free tier to research upstream changes for each
 * documentation repo, then creates Google Docs in your Drive.
 *
 * SETUP:
 *   1. Go to https://script.google.com → New Project
 *   2. Paste this entire file
 *   3. Set your API key:
 *      - Click ⚙️ Project Settings → Script Properties
 *      - Add: GEMINI_API_KEY = <your key from https://aistudio.google.com/apikey>
 *   4. Set your Drive folder ID:
 *      - Add: DRIVE_FOLDER_ID = <folder ID from your Drive URL>
 *   5. Run → doWeeklyResearch() to test
 *   6. Triggers → Add Trigger:
 *      - Function: doWeeklyResearch
 *      - Event: Time-driven → Week timer → Every Monday at 5-6 AM
 *
 * COST: $0. Uses Gemini API free tier (50 requests/day limit).
 */

// ============== CONFIGURATION ==============

var REPOS = {
    ClaudeCodeDocs: {
        name: "Anthropic Claude Code CLI",
        startUrl: "https://code.claude.com/docs/en/cli-reference",
        domains: "docs.anthropic.com, code.claude.com",
        feedUrl: "https://github.com/anthropics/claude-code/releases.atom",
    },
    GeminiDocs: {
        name: "Google Gemini CLI",
        startUrl: "https://geminicli.com/docs/",
        domains: "geminicli.com, ai.google.dev",
        feedUrl: "https://github.com/google-gemini/gemini-cli/releases.atom",
    },
    CodexDocs: {
        name: "OpenAI Codex CLI",
        startUrl: "https://developers.openai.com/codex/cli/",
        domains: "developers.openai.com",
        feedUrl: "https://github.com/openai/codex/releases.atom",
    },
    AntigravityDocs: {
        name: "Google Antigravity",
        startUrl: "https://antigravity.im/documentation",
        domains: "antigravity.google, antigravity.im",
        feedUrl: null,
    },
};

// ============== MAIN FUNCTION ==============

function doWeeklyResearch() {
    var apiKey = PropertiesService.getScriptProperties().getProperty("GEMINI_API_KEY");
    var folderId = PropertiesService.getScriptProperties().getProperty("DRIVE_FOLDER_ID");

    if (!apiKey) {
        Logger.log("ERROR: GEMINI_API_KEY not set in Script Properties");
        return;
    }

    // Create or find research folder
    if (!folderId) {
        var folders = DriveApp.getFoldersByName("DocMaintainer Research");
        if (folders.hasNext()) {
            folderId = folders.next().getId();
        } else {
            var folder = DriveApp.createFolder("DocMaintainer Research");
            folderId = folder.getId();
            PropertiesService.getScriptProperties().setProperty("DRIVE_FOLDER_ID", folderId);
        }
        Logger.log("Using folder: " + folderId);
    }

    var targetFolder = DriveApp.getFolderById(folderId);
    var dateStr = Utilities.formatDate(new Date(), "UTC", "yyyy-MM-dd");
    var allReports = [];

    for (var repoName in REPOS) {
        var config = REPOS[repoName];
        Logger.log("Researching: " + repoName);

        try {
            var report = callGeminiAPI(apiKey, buildPrompt(repoName, config));

            if (report) {
                // Create Google Doc
                var title = "Research: " + repoName + " — " + dateStr;
                var doc = DocumentApp.create(title);
                var body = doc.getBody();
                body.setText(report);
                doc.saveAndClose();

                // Move to research folder
                var file = DriveApp.getFileById(doc.getId());
                file.moveTo(targetFolder);

                Logger.log("  ✅ Created: " + title);
                allReports.push({ repo: repoName, docId: doc.getId(), status: "ok" });
            }
        } catch (e) {
            Logger.log("  ❌ Error for " + repoName + ": " + e.message);
            allReports.push({ repo: repoName, error: e.message, status: "error" });
        }
    }

    // Send summary email
    sendSummaryEmail(allReports, dateStr);

    Logger.log("Research complete: " + allReports.length + " reports");
}

// ============== GEMINI API ==============

// Best free-tier models with automatic fallback
// gemini-2.5-flash: 5 RPM free, best quality
// gemini-2.0-flash: 15 RPM free, good quality
// gemini-2.0-flash-lite: 30 RPM free, fast
var MODEL_CHAIN = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
];

function callGeminiAPI(apiKey, prompt) {
    var payload = {
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: {
            temperature: 0.3,
            maxOutputTokens: 4096,
        },
    };

    var options = {
        method: "post",
        contentType: "application/json",
        payload: JSON.stringify(payload),
        muteHttpExceptions: true,
    };

    // Try each model in the fallback chain
    for (var i = 0; i < MODEL_CHAIN.length; i++) {
        var model = MODEL_CHAIN[i];
        var url =
            "https://generativelanguage.googleapis.com/v1beta/models/" +
            model +
            ":generateContent?key=" +
            apiKey;

        Logger.log("  Trying model: " + model);
        var response = UrlFetchApp.fetch(url, options);
        var code = response.getResponseCode();

        if (code === 200) {
            var data = JSON.parse(response.getContentText());
            var candidates = data.candidates || [];
            if (candidates.length > 0 && candidates[0].content && candidates[0].content.parts) {
                Logger.log("  ✅ Success with " + model);
                return candidates[0].content.parts[0].text;
            }
            throw new Error("No content in API response");
        } else if (code === 429 && i < MODEL_CHAIN.length - 1) {
            Logger.log("  ⬇️ Rate limited on " + model + ", falling back...");
            Utilities.sleep(15000); // 15s cooldown
            continue;
        } else {
            throw new Error("API returned " + code + ": " + response.getContentText().substring(0, 300));
        }
    }

    throw new Error("All models exhausted (rate limited)");
}

// ============== PROMPT BUILDER ==============

function buildPrompt(repoName, config) {
    return (
        "You are a documentation research assistant. Research the latest updates for " +
        config.name +
        " and produce a structured report.\n\n" +
        "Sources to check:\n" +
        "- Official documentation: " + config.startUrl + "\n" +
        "- Official domains: " + config.domains + "\n" +
        (config.feedUrl ? "- GitHub releases: " + config.feedUrl + "\n" : "") +
        "\nReport structure:\n" +
        "1. Latest Version — Current release, breaking changes\n" +
        "2. New Features — Features added since last major release\n" +
        "3. Deprecations & Removals\n" +
        "4. Configuration Changes — New settings, flags, env vars\n" +
        "5. Experimental Features — Beta/preview items\n" +
        "6. Documentation Gaps — Thin pages or missing topics\n\n" +
        "Format as clean Markdown. Include CLI flags, config keys, code examples.\n" +
        "Repository: " + repoName + "\n" +
        "Date: " + Utilities.formatDate(new Date(), "UTC", "yyyy-MM-dd")
    );
}

// ============== EMAIL SUMMARY ==============

function sendSummaryEmail(results, dateStr) {
    var subject = "📋 DocMaintainer Research — " + dateStr;
    var body = "Weekly research complete.\n\n";

    for (var i = 0; i < results.length; i++) {
        var r = results[i];
        if (r.status === "ok") {
            body +=
                "✅ " +
                r.repo +
                ": https://docs.google.com/document/d/" +
                r.docId +
                "\n";
        } else {
            body += "❌ " + r.repo + ": " + r.error + "\n";
        }
    }

    body += "\n— DocMaintainer Automation";

    try {
        MailApp.sendEmail(Session.getActiveUser().getEmail(), subject, body);
    } catch (e) {
        Logger.log("Email send failed: " + e.message);
    }
}
