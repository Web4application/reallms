const express = require('express');
const { BotFrameworkAdapter } = require('botbuilder');
const { ScriptAnalyzerBot } = require('./bots/ScriptAnalyzerBot');

const adapter = new BotFrameworkAdapter({
    appId: process.env.MicrosoftAppId || '',
    appPassword: process.env.MicrosoftAppPassword || ''
});

const bot = new ScriptAnalyzerBot();
const app = express();
app.use(express.json());

app.post('/api/messages', (req, res) => {
    adapter.processActivity(req, res, async (context) => {
        await bot.run(context);
    });
});

const port = process.env.PORT || 3000;
app.listen(port, () => 
    console.log(`🤖 Bot is running at http://127.0.0.1:${3000}/api/messages`);
});
