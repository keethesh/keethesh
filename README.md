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

![GitHub Chat](chat-display.svg)


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
    animation: slideIn 0.6s ease-out;
    position: relative;
    overflow: hidden;
}

.chat-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    background-size: 200% 100%;
    animation: shimmer 3s infinite;
    pointer-events: none;
    opacity: 0.3;
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
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
}

.window-control:hover {
    transform: scale(1.1);
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.window-controls:hover .control-close {
    animation: pulse 1.5s infinite;
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
    animation: typing 2s infinite;
}

.header-meta.active {
    animation: typing 1.5s infinite;
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
    transition: all 0.2s ease;
    animation: fadeIn 0.4s ease-out;
}

.reaction:hover {
    background: #e1e8ed;
    transform: scale(1.05);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.reaction-emoji {
    font-size: 14px;
    animation: breathe 3s ease-in-out infinite;
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
    animation: slideIn 0.8s ease-out 0.3s both;
    position: relative;
}

.chat-footer::before {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, #0969da, #8250df);
    animation: expandLine 2s ease-out 1s forwards;
    transform: translateX(-50%);
}

@keyframes expandLine {
    to { width: 60%; }
}

.join-link {
    color: #0969da;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
    position: relative;
    display: inline-block;
}

.join-link:hover {
    text-decoration: none;
    transform: translateY(-1px);
    color: #0550ae;
}

.join-link::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, #0969da, #8250df);
    transition: width 0.3s ease;
}

.join-link:hover::after {
    width: 100%;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

@keyframes breathe {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes typing {
    0%, 60% { opacity: 1; }
    30% { opacity: 0.4; }
    100% { opacity: 1; }
}

@keyframes slideIn {
    from { transform: translateX(-10px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* Respect reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
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
    
    .chat-header::before {
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
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
<div class="header-meta active">4 users active • 13:18:49</div>
</div>
<div class="chat-messages">
<div class="message owner">
<div class="message-header">
<a href="https://github.com/keethesh" class="username owner" target="_blank" rel="noopener">@keethesh</a>
<span class="timestamp">11:24</span>
</div>
<div class="message-content">This is the first message</div>
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
