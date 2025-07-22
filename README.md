<!-- GitHub profile README -->
<h1 align="center">Hey, I’m Keethesh 👋</h1>
<p align="center">
  🇲🇺 22-year-old polymathic builder · CISSP 🛡️ · Always curious, always iterating
</p>

---

### 🚢  Now Shipping
- **[LookbackAI](https://lookbackai.com)** - AI-powered video-journal SaaS that tracks growth from facial, vocal & linguistic cues 📈  
- **Planify** - Motion-style planner where you put real cash 💸 on the line to finish tasks (skin-in-the-game productivity)  
- **MergeFleet** - Unity mobile game prototype: merge, upgrade & command your own space armada 🎮🛸  

### 🧰  Everyday Tools
`Python` · `TypeScript` · `React / Next.js` · `Unity / C#`  
Detours into `Ghidra`, `radare2`, `Binary Ninja`. Whatever the mission calls for 🔍

### 🪐  Interests & Skills
| 💡 Logic & Tech | 🛠️ Hands-On | 🎵 / 🎨 Creative | 🏃‍♂️ Motion |
|-----------------|-------------|-----------------|--------------|
| Pentesting & OSINT | Lockpicking & electronics | Beatmaking | Calisthenics |
| Reverse engineering | Mechanical Engineering | Photography & editing | Skateboarding |
| AI / data pipelines | Rope & knotwork | Storycraft & UX | Muay Thai |
| AV/EDR Evasion & Bypass | Welding | 3D Modeling | Football Freestyle |

<sub>My curiosity never skips leg day.</sub>

### 💬 Community Chat
Join the conversation! Comment on [Issue #2](https://github.com/keethesh/keethesh/issues/2) to see your message appear here.

<!-- CHAT_START -->

<style>
.chat-container {
    max-width: 600px;
    margin: 0 auto;
    border: 1px solid #d1d9e0;
    border-radius: 8px;
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.chat-header {
    background: linear-gradient(135deg, #f6f8fa 0%, #e1e8ed 100%);
    border-bottom: 1px solid #d1d9e0;
    padding: 12px 16px;
    border-radius: 8px 8px 0 0;
}

.window-controls {
    display: inline-flex;
    gap: 6px;
    margin-right: 12px;
    align-items: center;
}

.window-control {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
}

.control-close { background: #ff5f57; }
.control-minimize { background: #ffbd2e; }
.control-maximize { background: #28ca42; }

.header-title {
    font-weight: 600;
    color: #24292f;
    display: inline;
}

.header-meta {
    font-size: 12px;
    color: #656d76;
    margin-top: 4px;
}

.chat-messages {
    padding: 16px;
    min-height: 200px;
    max-height: 400px;
    overflow-y: auto;
}

.message {
    margin-bottom: 16px;
    animation: fadeIn 0.3s ease-in;
}

.message:last-child {
    margin-bottom: 0;
}

.message-header {
    display: flex;
    align-items: center;
    margin-bottom: 4px;
    gap: 8px;
}

.avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 2px solid #d1d9e0;
    transition: border-color 0.2s ease;
}

.avatar:hover {
    border-color: #0969da;
}

.avatar.owner {
    border-color: #8250df;
}

.message-reactions {
    margin-top: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.reaction {
    background: #f6f8fa;
    border: 1px solid #d1d9e0;
    border-radius: 16px;
    padding: 4px 8px;
    font-size: 12px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    transition: background-color 0.2s ease;
}

.reaction:hover {
    background: #e1e8ed;
}

.reaction-emoji {
    font-size: 14px;
}

.reaction-count {
    color: #656d76;
    font-weight: 500;
}

.username {
    font-weight: 600;
    color: #0969da;
    font-size: 14px;
    text-decoration: none;
    transition: color 0.2s ease;
}

.username:hover {
    text-decoration: underline;
}

.username.owner {
    color: #8250df;
}

.username.owner:hover {
    color: #6639ba;
}

.timestamp {
    font-size: 12px;
    color: #656d76;
}

.message-content {
    background: #f6f8fa;
    padding: 8px 12px;
    border-radius: 8px;
    border-left: 3px solid #d1d9e0;
    line-height: 1.4;
    color: #24292f;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

.message.owner .message-content {
    background: #dbeafe;
    border-left-color: #0969da;
}

.empty-state {
    text-align: center;
    padding: 32px 16px;
    color: #656d76;
}

.project-showcase {
    background: #f6f8fa;
    border-radius: 6px;
    padding: 12px;
    margin: 12px 0;
    border-left: 3px solid #fd8c73;
}

.project-item {
    margin: 6px 0;
    font-size: 14px;
}

.chat-footer {
    background: #f6f8fa;
    border-top: 1px solid #d1d9e0;
    padding: 12px 16px;
    border-radius: 0 0 8px 8px;
    text-align: center;
    font-size: 14px;
    color: #656d76;
}

.join-link {
    color: #0969da;
    text-decoration: none;
    font-weight: 500;
}

.join-link:hover {
    text-decoration: underline;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .chat-container {
        background: #0d1117;
        border-color: #30363d;
    }
  
    .chat-header {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        border-bottom-color: #30363d;
    }
  
    .header-title { color: #f0f6fc; }
    .header-meta { color: #8b949e; }
  
    .message-content {
        background: #161b22;
        border-left-color: #30363d;
        color: #f0f6fc;
    }
  
    .message.owner .message-content {
        background: #0c2d6b;
        border-left-color: #1f6feb;
    }
  
    .username { color: #58a6ff; }
    .username:hover { color: #79c0ff; }
    .username.owner { color: #a5a3ff; }
    .username.owner:hover { color: #b8b5ff; }
    .timestamp { color: #8b949e; }
  
    .project-showcase {
        background: #161b22;
        border-left-color: #f85149;
    }
  
    .chat-footer {
        background: #161b22;
        border-top-color: #30363d;
        color: #8b949e;
    }
  
    .empty-state {
        color: #8b949e;
    }
  
    .join-link {
        color: #58a6ff;
    }
    
    .avatar {
        border-color: #30363d;
    }
    
    .avatar:hover {
        border-color: #58a6ff;
    }
    
    .avatar.owner {
        border-color: #a5a3ff;
    }
    
    .reaction {
        background: #161b22;
        border-color: #30363d;
    }
    
    .reaction:hover {
        background: #21262d;
    }
    
    .reaction-count {
        color: #8b949e;
    }
}
</style>
<div class="chat-container">
<div class="chat-header">
<div class="window-controls">
<span class="window-control control-close"></span>
<span class="window-control control-minimize"></span>
<span class="window-control control-maximize"></span>
</div>
<div class="header-title">#readme-chat</div>
<div class="header-meta">4 users active • 13:01:55</div>
</div>
<div class="chat-messages">
<div class="message owner">
<div class="message-header">
<img src="https://github.com/keethesh.png?size=32" alt="keethesh avatar" class="avatar owner" loading="lazy">
<a href="https://github.com/keethesh" class="username owner" target="_blank" rel="noopener">@keethesh</a>
<span class="timestamp">11:47</span>
</div>
<div class="message-content">Thanks! The facial recognition is hitting 94% accuracy now. Still tuning the vocal cues...</div>
</div>
<div class="message">
<div class="message-header">
<img src="https://github.com/bob_sec.png?size=32" alt="bob_sec avatar" class="avatar" loading="lazy">
<a href="https://github.com/bob_sec" class="username" target="_blank" rel="noopener">@bob_sec</a>
<span class="timestamp">12:15</span>
</div>
<div class="message-content">Any plans for CISSP study groups?</div>
</div>
<div class="message">
<div class="message-header">
<img src="https://github.com/charlie_ml.png?size=32" alt="charlie_ml avatar" class="avatar" loading="lazy">
<a href="https://github.com/charlie_ml" class="username" target="_blank" rel="noopener">@charlie_ml</a>
<span class="timestamp">14:32</span>
</div>
<div class="message-content">This is absolutely fascinating! I&#x27;ve been diving deep into your LookbackAI project and the technical implementation is genuinely impressive. The facial recognition accuracy you mentioned (94%) is remarkable for real-time processing. I&#x27;m particularly curious about how you&#x27;re handling edge cases with varying lighting conditions and different facial angles. The vocal cue analysis component sounds like an innovative approach to emotion detection. Have you considered implementing ensemble methods...</div>
</div>
<div class="message">
<div class="message-header">
<img src="https://github.com/david_devops.png?size=32" alt="david_devops avatar" class="avatar" loading="lazy">
<a href="https://github.com/david_devops" class="username" target="_blank" rel="noopener">@david_devops</a>
<span class="timestamp">15:45</span>
</div>
<div class="message-content">Quick question about deployment! Looking at Docker + Kubernetes for production. Any thoughts on scaling strategies?</div>
</div>
</div>
<div class="chat-footer">
💬 <a href="https://github.com/keethesh/keethesh/issues/2" class="join-link" target="_blank">
Join the conversation in Issue #2</a>
</div>
</div>
<!-- CHAT_END -->

### 🧠 Latest Learnings

<!-- TIL_START -->
* [Getting started](til/001-getting-started.md)
<!-- TIL_END -->

### 📫  Elsewhere
[LinkedIn](https://www.linkedin.com/in/keethesh)

---

<p align="center"><em>Start bold, polish later.</em></p>
