# Facebook MCP Server

This project is a **MCP server** for automating and managing interactions on a Facebook Page using the Facebook Graph API. It exposes tools to create posts, moderate comments, fetch post insights, and filter negative feedback — ready to plug into Claude, or other LLM-based agents.

[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/HagaiHen/facebook-mcp-server)](https://archestra.ai/mcp-catalog/hagaihen__facebook-mcp-server)
<a href="https://glama.ai/mcp/servers/@HagaiHen/facebook-mcp-server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@HagaiHen/facebook-mcp-server/badge" />
</a>

---

## 🤖 What Is This?

This MCP provides a suite of AI-callable tools that connect directly to a Facebook Page, abstracting common API operations as LLM-friendly functions.

### ✅ Benefits

- Empowers **social media managers** to automate moderation and analytics.
- Seamlessly integrates with **Claude Desktop or any Agent client**.
- Enables fine-grained control over Facebook content from natural language.

---

## 📦 Features

| Tool                             | Description                                                         |
|----------------------------------|---------------------------------------------------------------------|
| `post_to_facebook`               | Create a new Facebook post with a message.                          |
| `reply_to_comment`               | Reply to a specific comment on a post.                              |
| `get_page_posts`                 | Retrieve recent posts from the Page.                                |
| `get_post_comments`              | Fetch comments on a given post.                                     |
| `delete_post`                    | Delete a specific post by ID.                                       |
| `delete_comment`                 | Delete a specific comment by ID.                                    |
| `hide_comment`                   | Hide a comment from public view.                         |
| `unhide_comment`                 | Unhide a previously hidden comment.                      |
| `delete_comment_from_post`       | Alias for deleting a comment from a specific post.                  |
| `filter_negative_comments`       | Filter out comments with negative sentiment keywords.               |
| `get_number_of_comments`         | Count the number of comments on a post.                             |
| `get_number_of_likes`            | Count the number of likes on a post.                                |
| `get_post_impressions`           | Get total impressions on a post.                                    |
| `get_post_impressions_unique`    | Get number of unique users who saw the post.                        |
| `get_post_impressions_paid`      | Get number of paid impressions on the post.                         |
| `get_post_impressions_organic`   | Get number of organic impressions on the post.                      |
| `get_post_engaged_users`         | Get number of users who engaged with the post.                      |
| `get_post_clicks`                | Get number of clicks on the post.                                   |
| `get_post_reactions_like_total`  | Get total number of 'Like' reactions.                               |
| `get_post_top_commenters`        | Get the top commenters on a post.                                   |
| `post_image_to_facebook`         | Post an image with a caption to the Facebook page.                  |
| `send_dm_to_user`                | Send a direct message to a user.                                    |
| `update_post`                    | Updates an existing post's message.                                 |
| `schedule_post`                  | Schedule a post for future publication.                     |
| `get_page_fan_count`             | Retrieve the total number of Page fans.                     |
| `get_post_share_count`           | Get the number of shares on a post.                         |
| `get_post_reactions_breakdown`   | Get all reaction counts for a post in one call.              |
| `bulk_delete_comments`           | Delete multiple comments by ID.                              |
| `bulk_hide_comments`             | Hide multiple comments by ID.                    |
| `create_page_media_post`         | 🔥 **NEW** Create viral media posts on specific pages with auto-generated copyright text. |
| `post_media_to_facebook`         | Post multiple media files with auto-generated viral copyright text. |
| `post_video_to_facebook`         | Post videos with viral copyright text generated from content description. |
| `create_storie_list_media`       | Create Facebook Stories from a list of media URLs. |
| `send_dm_media_to_user`          | Send direct messages with media attachments to users. |
| `get_my_stories`                 | Get recent stories from your Facebook page. |
| `get_my_last_post`               | Get your most recent post with comprehensive engagement metrics. |

---

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/facebook-mcp-server.git
cd facebook-mcp-server
```

### 2. 🛠️ Installation

Install dependencies using uv, a fast Python package manager:
If uv is not already installed, run:
```bash
curl -Ls https://astral.sh/uv/install.sh | bash
```

Once uv is installed, install the project dependencies:
```bash
uv pip install -r requirements.txt
```

### 3. Set Up Environment

Create a .env file in the root directory and add your Facebook Page credentials. 
You can obtain these from  https://developers.facebook.com/tools/explorer

```bash
FACEBOOK_ACCESS_TOKEN=your_facebook_page_access_token
FACEBOOK_PAGE_ID=your_page_id
```

## 🧩 Using with Claude Desktop
To set up the FacebookMCP in Clade:

1.	Open Clade.
2.	Go to Settings → Developer → Edit Config.
3.	In the config file that opens, add the following entry:

```bash
"FacebookMCP": {
  "command": "uv",
  "args": [
    "run",
    "--with",
    "mcp[cli]",
    "--with",
    "requests",
    "mcp",
    "run",
    "/path/to/facebook-mcp-server/server.py"
  ]
}
```

---

## ✅ You’re Ready to Go!

That’s it — your Facebook MCP server is now fully configured and ready to power Claude Desktop. You can now post, moderate, and measure engagement all through natural language prompts!

---

## 🔥 NEW: create_page_media_post Tool

### The Ultimate Viral Content Creator

The new `create_page_media_post` tool is a game-changer for social media marketing. It combines:

- **🎯 Page-Specific Posting**: Target any Facebook page by ID
- **🚀 Viral Text Generation**: Auto-creates engaging copyright text with emojis, legal notices, and call-to-actions
- **📱 Multi-Media Support**: Handles images, videos, and mixed content seamlessly
- **⚡ Instant Engagement**: Built-in viral elements designed to maximize likes, shares, and comments
- **🛡️ Copyright Protection**: Automatic legal notices and usage terms

#### Example Usage:
```python
create_page_media_post(
    page_id="123456789012345",
    media_urls=["image1.jpg", "video1.mp4"],
    content_prompt="Tutorial de cocina italiana casera"
)
```

**Generated Viral Text Example:**
```
🔥 TUTORIAL DE COCINA ITALIANA CASERA 🔥

✨ CONTENIDO ORIGINAL EXCLUSIVO ✨

© Todos los derechos reservados. Este contenido es propiedad intelectual protegida.

🚫 PROHIBIDA su reproducción, distribución o uso sin autorización expresa.
✅ SÍ se permite compartir desde esta publicación

💯 ¡COMPARTE si te gustó! 👇

#ViralContent #Original #Copyright #Exclusive #Trending
```

See `CREATE_PAGE_MEDIA_POST_DOCS.md` for complete documentation and examples.

---

## 💰 Million-Dollar Use Cases of Facebook MCP

The Facebook Marketing Cloud Platform (MCP) offers a powerful suite of tools that, when leveraged effectively, can translate into significant financial gains and operational efficiencies for businesses. Here are some "million-dollar" use cases:

### 1. Automated Customer Support & Engagement

By integrating the MCP with AI agents, businesses can automate responses to comments and direct messages. This dramatically reduces customer service costs, improves response times, and enhances customer satisfaction. For example, AI can automatically hide negative comments, reply to common queries, and even escalate complex issues to human agents, ensuring a seamless customer experience at scale.

### 2. Hyper-Targeted Advertising & Campaign Optimization

The MCP provides granular insights into post performance, audience demographics, and engagement patterns. Businesses can use this data to:
- Identify top-performing content and replicate its success.
- Understand which reactions (likes, loves, wows) are most prevalent and tailor content to evoke desired emotions.
- Optimize ad spend by targeting users who have previously engaged with content, leading to higher conversion rates and lower customer acquisition costs.

### 3. Influencer Marketing & Community Building

The `get_post_top_commenters` tool can identify highly engaged users and potential brand advocates. This allows businesses to:
- Discover micro-influencers within their existing audience.
- Foster stronger community relationships by directly engaging with top contributors.
- Collaborate with influential users to amplify marketing messages organically, leading to increased brand awareness and sales without traditional advertising costs.

### 4. Brand Reputation Management & Crisis Prevention

The `filter_negative_comments` and `hide_comment` tools are crucial for maintaining a positive brand image. By automating the detection and moderation of negative or spammy comments, businesses can:
- Quickly mitigate PR crises before they escalate.
- Protect brand reputation by ensuring only positive and constructive discussions are publicly visible.
- Reduce the labor required for manual content moderation, freeing up resources for more strategic tasks.

### 5. Data-Driven Content Strategy

Analyzing post insights such as `get_post_impressions_unique`, `get_post_clicks`, and `get_post_share_count` provides invaluable data for content strategists. This enables businesses to:
- Understand which content formats and topics resonate most with their audience.
- Refine their content calendar to produce more engaging and shareable posts.
- Measure the true ROI of their content efforts by correlating engagement metrics with business outcomes, leading to more effective and profitable content strategies.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to fork the repo and submit a pull request.

- Create a branch: `git checkout -b feature/YourFeature`
- Commit your changes: `git commit -m 'feat: add new feature'`
- Push to the branch: `git push origin feature/YourFeature`
- Open a pull request 🎉
