import requests
from typing import Any
from config import GRAPH_API_BASE_URL, PAGE_ID, PAGE_ACCESS_TOKEN


class FacebookAPI:
    # Generic Graph API request method
    def _request(self, method: str, endpoint: str, params: dict[str, Any], json: dict[str, Any] = None) -> dict[str, Any]:
        url = f"{GRAPH_API_BASE_URL}/{endpoint}"
        params["access_token"] = PAGE_ACCESS_TOKEN
        response = requests.request(method, url, params=params, json=json)
        return response.json()

    def post_message(self, message: str) -> dict[str, Any]:
        return self._request("POST", f"{PAGE_ID}/feed", {"message": message})

    def reply_to_comment(self, comment_id: str, message: str) -> dict[str, Any]:
        return self._request("POST", f"{comment_id}/comments", {"message": message})

    def get_posts(self) -> dict[str, Any]:
        return self._request("GET", f"{PAGE_ID}/posts", {"fields": "id,message,created_time"})

    def get_comments(self, post_id: str) -> dict[str, Any]:
        return self._request("GET", f"{post_id}/comments", {"fields": "id,message,from,created_time"})

    def delete_post(self, post_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"{post_id}", {})

    def delete_comment(self, comment_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"{comment_id}", {})

    def hide_comment(self, comment_id: str) -> dict[str, Any]:
        """Hide a comment from the Page."""
        return self._request("POST", f"{comment_id}", {"is_hidden": True})

    def unhide_comment(self, comment_id: str) -> dict[str, Any]:
        """Unhide a previously hidden comment."""
        return self._request("POST", f"{comment_id}", {"is_hidden": False})

    def get_insights(self, post_id: str, metric: str, period: str = "lifetime") -> dict[str, Any]:
        return self._request("GET", f"{post_id}/insights", {"metric": metric, "period": period})

    def get_bulk_insights(self, post_id: str, metrics: list[str], period: str = "lifetime") -> dict[str, Any]:
        metric_str = ",".join(metrics)
        return self.get_insights(post_id, metric_str, period)

    def post_image_to_facebook(self, image_url: str, caption: str) -> dict[str, Any]:
        params = {
            "url": image_url,
            "caption": caption
        }
        return self._request("POST", f"{PAGE_ID}/photos", params)
    
    def send_dm_to_user(self, user_id: str, message: str) -> dict[str, Any]:
        payload = {
            "recipient": {"id": user_id},
            "message": {"text": message},
            "messaging_type": "RESPONSE"
        }
        return self._request("POST", "me/messages", {}, json=payload)
    
    def send_dm_media_to_user(self, user_id: str, message: str, media_urls: list[str]) -> dict[str, Any]:
        """Send a direct message with media attachments to a user.
        
        Args:
            user_id: The recipient's Facebook user ID
            message: Text message to send
            media_urls: List of URLs to images or videos (local file paths or HTTPS URLs)
        
        Returns:
            dict: Response from Facebook Messenger API
        """
        # First send the text message
        text_response = self.send_dm_to_user(user_id, message)
        
        # Then send each media attachment
        media_responses = []
        for media_url in media_urls:
            # Determine if it's an image or video based on file extension
            media_type = self._get_media_type(media_url)
            
            if media_type == "image":
                payload = {
                    "recipient": {"id": user_id},
                    "message": {
                        "attachment": {
                            "type": "image",
                            "payload": {"url": media_url, "is_reusable": True}
                        }
                    },
                    "messaging_type": "RESPONSE"
                }
            elif media_type == "video":
                payload = {
                    "recipient": {"id": user_id},
                    "message": {
                        "attachment": {
                            "type": "video",
                            "payload": {"url": media_url, "is_reusable": True}
                        }
                    },
                    "messaging_type": "RESPONSE"
                }
            else:
                # Fallback to file attachment for other types
                payload = {
                    "recipient": {"id": user_id},
                    "message": {
                        "attachment": {
                            "type": "file",
                            "payload": {"url": media_url, "is_reusable": True}
                        }
                    },
                    "messaging_type": "RESPONSE"
                }
            
            response = self._request("POST", "me/messages", {}, json=payload)
            media_responses.append({"media_url": media_url, "response": response})
        
        return {
            "text_message": text_response,
            "media_messages": media_responses,
            "total_media_sent": len(media_urls)
        }
    
    def _get_media_type(self, url: str) -> str:
        """Determine media type based on file extension."""
        url_lower = url.lower()
        if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            return "image"
        elif any(ext in url_lower for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']):
            return "video"
        else:
            return "file"
    
    def update_post(self, post_id: str, new_message: str) -> dict[str, Any]:
        return self._request("POST", f"{post_id}", {"message": new_message})

    def schedule_post(self, message: str, publish_time: int) -> dict[str, Any]:
        params = {
            "message": message,
            "published": False,
            "scheduled_publish_time": publish_time,
        }
        return self._request("POST", f"{PAGE_ID}/feed", params)

    def get_page_fan_count(self) -> int:
        data = self._request("GET", f"{PAGE_ID}", {"fields": "fan_count"})
        return data.get("fan_count", 0)

    def get_post_share_count(self, post_id: str) -> int:
        data = self._request("GET", f"{post_id}", {"fields": "shares"})
        return data.get("shares", {}).get("count", 0)
    
    def create_storie_list_media(self, media_urls: list[str]) -> dict[str, Any]:
        """Create and publish Facebook Stories from a list of media URLs.
        
        Args:
            media_urls: List of URLs to images or videos (local file paths or HTTPS URLs)
        
        Returns:
            dict: Response with results from all story creations
        """
        story_responses = []
        
        for media_url in media_urls:
            media_type = self._get_media_type(media_url)
            
            if media_type == "image":
                # Create image story
                params = {
                    "source": media_url,
                    "published": True
                }
                response = self._request("POST", f"{PAGE_ID}/photos", params)
                
            elif media_type == "video":
                # Create video story
                params = {
                    "source": media_url,
                    "published": True,
                    "content_category": "OTHER"
                }
                response = self._request("POST", f"{PAGE_ID}/videos", params)
                
            else:
                # Skip unsupported file types for stories
                response = {
                    "error": f"Unsupported media type for story: {media_url}",
                    "supported_formats": "Images: JPG, PNG, GIF, WebP | Videos: MP4, MOV, AVI, MKV, WebM"
                }
            
            story_responses.append({
                "media_url": media_url,
                "media_type": media_type,
                "response": response
            })
        
        return {
            "stories_created": len([r for r in story_responses if "error" not in r["response"]]),
            "total_media_processed": len(media_urls),
            "results": story_responses
        }
    
    def get_my_stories(self, limit: int = None) -> dict[str, Any]:
        """Get the list of recent stories from the page.
        
        Args:
            limit: Optional number of stories to retrieve. If None, gets all available stories.
        
        Returns:
            dict: Response with list of stories and metadata
        """
        # Build parameters for the API request
        params = {
            "fields": "id,created_time,permalink_url,media_type,media_url,thumbnail_url"
        }
        
        # Add limit if specified by user
        if limit is not None and limit > 0:
            params["limit"] = limit
        
        # Get stories from the page
        # Note: Facebook Graph API uses different endpoints for stories
        # We'll try to get recent media posts that could include stories
        try:
            # First try to get stories directly (if available)
            stories_response = self._request("GET", f"{PAGE_ID}/stories", params)
            
            # If stories endpoint doesn't work, fallback to recent media
            if "error" in stories_response:
                # Fallback: get recent photos and videos which might include story content
                media_params = {
                    "fields": "id,created_time,permalink_url,source,images,videos,caption",
                    "type": "uploaded"
                }
                if limit is not None and limit > 0:
                    media_params["limit"] = limit
                
                photos_response = self._request("GET", f"{PAGE_ID}/photos", media_params)
                videos_response = self._request("GET", f"{PAGE_ID}/videos", media_params)
                
                # Combine and format the results
                all_media = []
                
                # Add photos
                if "data" in photos_response:
                    for photo in photos_response["data"]:
                        all_media.append({
                            "id": photo.get("id"),
                            "created_time": photo.get("created_time"),
                            "permalink_url": photo.get("permalink_url"),
                            "media_type": "photo",
                            "media_url": photo.get("source"),
                            "thumbnail_url": photo.get("images", [{}])[0].get("source") if photo.get("images") else None,
                            "caption": photo.get("caption", "")
                        })
                
                # Add videos
                if "data" in videos_response:
                    for video in videos_response["data"]:
                        all_media.append({
                            "id": video.get("id"),
                            "created_time": video.get("created_time"),
                            "permalink_url": video.get("permalink_url"),
                            "media_type": "video",
                            "media_url": video.get("source"),
                            "thumbnail_url": video.get("picture"),
                            "caption": video.get("description", "")
                        })
                
                # Sort by creation time (most recent first)
                all_media.sort(key=lambda x: x.get("created_time", ""), reverse=True)
                
                # Apply limit if specified
                if limit is not None and limit > 0:
                    all_media = all_media[:limit]
                
                return {
                    "data": all_media,
                    "total_count": len(all_media),
                    "limit_applied": limit,
                    "source": "fallback_media_endpoint",
                    "message": "Retrieved recent media content (photos and videos) as story data"
                }
            
            # If stories endpoint worked, return the stories
            stories_data = stories_response.get("data", [])
            return {
                "data": stories_data,
                "total_count": len(stories_data),
                "limit_applied": limit,
                "source": "stories_endpoint",
                "message": f"Retrieved {len(stories_data)} stories from page"
            }
            
        except Exception as e:
            return {
                "error": f"Failed to retrieve stories: {str(e)}",
                "data": [],
                "total_count": 0,
                "limit_applied": limit
            }
    
    def get_my_last_post(self) -> dict[str, Any]:
        """Get the most recent post from the page.
        
        Returns:
            dict: Response with the last post data and metadata
        """
        try:
            # Get the most recent post with comprehensive fields
            params = {
                "fields": "id,message,created_time,updated_time,permalink_url,full_picture,picture,type,status_type,story,description,caption,name,link,source,place,privacy,shares,likes.summary(true),comments.summary(true),reactions.summary(true)",
                "limit": 1  # Only get the most recent post
            }
            
            response = self._request("GET", f"{PAGE_ID}/posts", params)
            
            if "error" in response:
                return {
                    "error": f"Failed to retrieve last post: {response.get('error', {}).get('message', 'Unknown error')}",
                    "data": None,
                    "found": False
                }
            
            posts_data = response.get("data", [])
            
            if not posts_data:
                return {
                    "message": "No posts found on this page",
                    "data": None,
                    "found": False,
                    "total_posts_on_page": 0
                }
            
            # Get the first (most recent) post
            last_post = posts_data[0]
            
            # Enhance the post data with additional metrics
            enhanced_post = {
                "id": last_post.get("id"),
                "message": last_post.get("message", ""),
                "created_time": last_post.get("created_time"),
                "updated_time": last_post.get("updated_time"),
                "permalink_url": last_post.get("permalink_url"),
                "full_picture": last_post.get("full_picture"),
                "picture": last_post.get("picture"),
                "type": last_post.get("type"),
                "status_type": last_post.get("status_type"),
                "story": last_post.get("story", ""),
                "description": last_post.get("description", ""),
                "caption": last_post.get("caption", ""),
                "name": last_post.get("name", ""),
                "link": last_post.get("link"),
                "source": last_post.get("source"),
                "place": last_post.get("place"),
                "privacy": last_post.get("privacy", {}),
                
                # Engagement metrics
                "likes_count": last_post.get("likes", {}).get("summary", {}).get("total_count", 0),
                "comments_count": last_post.get("comments", {}).get("summary", {}).get("total_count", 0),
                "reactions_count": last_post.get("reactions", {}).get("summary", {}).get("total_count", 0),
                "shares_count": last_post.get("shares", {}).get("count", 0),
                
                # Raw engagement data for detailed analysis
                "engagement_summary": {
                    "likes": last_post.get("likes", {}).get("summary", {}),
                    "comments": last_post.get("comments", {}).get("summary", {}),
                    "reactions": last_post.get("reactions", {}).get("summary", {}),
                    "shares": last_post.get("shares", {})
                }
            }
            
            return {
                "data": enhanced_post,
                "found": True,
                "message": "Successfully retrieved the most recent post",
                "post_age_info": {
                    "created_time": enhanced_post["created_time"],
                    "last_updated": enhanced_post["updated_time"]
                },
                "engagement_totals": {
                    "total_likes": enhanced_post["likes_count"],
                    "total_comments": enhanced_post["comments_count"], 
                    "total_reactions": enhanced_post["reactions_count"],
                    "total_shares": enhanced_post["shares_count"],
                    "total_engagement": enhanced_post["likes_count"] + enhanced_post["comments_count"] + enhanced_post["reactions_count"] + enhanced_post["shares_count"]
                }
            }
            
        except Exception as e:
            return {
                "error": f"Exception occurred while retrieving last post: {str(e)}",
                "data": None,
                "found": False
            }
    
    def post_video_to_facebook(self, video_url: str, content_prompt: str) -> dict[str, Any]:
        """Post a video with viral copyright text generated from a content prompt.
        
        Args:
            video_url: URL to the video (local file path or HTTPS URL)
            content_prompt: Description of the video content to generate viral copyright text
        
        Returns:
            dict: Response from Facebook Graph API with generated copyright text
        """
        # Verify it's a video file
        media_type = self._get_media_type(video_url)
        
        if media_type != "video":
            return {
                "error": f"Invalid media type. Expected video, got: {media_type}",
                "supported_formats": "Videos: MP4, MOV, AVI, MKV, WebM",
                "provided_url": video_url
            }
        
        # Generate viral copyright text based on content prompt
        viral_copyright_text = self._generate_viral_copyright_text(content_prompt)
        
        # Post video with generated copyright text
        params = {
            "source": video_url,
            "description": viral_copyright_text,
            "published": True,
            "content_category": "OTHER"
        }
        
        response = self._request("POST", f"{PAGE_ID}/videos", params)
        
        # Add the generated text to the response for reference
        if "error" not in response:
            response["generated_copyright_text"] = viral_copyright_text
            response["original_prompt"] = content_prompt
        
        return response
    
    def _generate_viral_copyright_text(self, content_prompt: str) -> str:
        """Generate viral copyright text based on content description.
        
        Args:
            content_prompt: Description of the video content
            
        Returns:
            str: Generated viral copyright text for Facebook
        """
        # Viral copyright text templates with engaging elements
        viral_templates = [
            f"🔥 {content_prompt} 🔥\n\n✨ CONTENIDO ORIGINAL EXCLUSIVO ✨\n\n© Todos los derechos reservados. Este video es propiedad intelectual protegida.\n\n🚫 PROHIBIDA su reproducción, distribución o uso sin autorización expresa.\n\n💯 ¡COMPARTE si te gustó! 👇\n\n#ViralContent #Original #Copyright #Exclusive",
            
            f"🎬 {content_prompt} 🎬\n\n⚡ CONTENIDO VIRAL ORIGINAL ⚡\n\n🔒 Material protegido por derechos de autor\n© Creación original - Todos los derechos reservados\n\n❌ NO se permite copiar, descargar o redistribuir\n✅ SÍ se permite compartir desde esta publicación\n\n🔥 ¡Dale LIKE y COMPARTE! 🔥\n\n#Viral #Original #Protected #ShareDontSteal",
            
            f"💥 {content_prompt} 💥\n\n🌟 CONTENIDO EXCLUSIVO Y ORIGINAL 🌟\n\n⚠️ AVISO LEGAL:\n© Este video está protegido por derechos de autor\n🚫 Prohibida su descarga o reutilización\n✅ Permitido compartir desde aquí\n\n🔥 ¡Si te encantó, COMPÁRTELO! 🔥\n👆 ¡Y no olvides seguirnos para más contenido!\n\n#ExclusiveContent #Copyright #ViralVideo #Original",
            
            f"🚀 {content_prompt} 🚀\n\n✨ MATERIAL ORIGINAL PROTEGIDO ✨\n\n📝 TÉRMINOS DE USO:\n• © Contenido con derechos reservados\n• 🚫 No descargar ni reutilizar\n• ✅ Compartir desde esta publicación\n• 💬 Comentar y etiquetar amigos\n\n🔥 ¡HAZLO VIRAL compartiendo! 🔥\n\n#OriginalContent #Viral #Copyright #ShareTheJoy"
        ]
        
        # Select a random template or rotate based on content
        import random
        selected_template = random.choice(viral_templates)
        
        return selected_template
    
    def post_media_to_facebook(self, media_urls: list[str], content_prompt: str) -> dict[str, Any]:
        """Post multiple media files (images/videos) with auto-generated viral copyright text.
        
        Args:
            media_urls: List of URLs to images or videos (local file paths or HTTPS URLs)
            content_prompt: Description of the media content to generate viral copyright text
        
        Returns:
            dict: Response with results from all media posts and generated copyright text
        """
        if not media_urls:
            return {
                "error": "No media URLs provided",
                "message": "At least one media URL is required"
            }
        
        # Generate viral copyright text based on content prompt
        viral_copyright_text = self._generate_viral_copyright_text(content_prompt)
        
        # Separate images and videos
        images = []
        videos = []
        unsupported = []
        
        for media_url in media_urls:
            media_type = self._get_media_type(media_url)
            if media_type == "image":
                images.append(media_url)
            elif media_type == "video":
                videos.append(media_url)
            else:
                unsupported.append(media_url)
        
        # Results container
        results = {
            "generated_copyright_text": viral_copyright_text,
            "original_prompt": content_prompt,
            "total_media_processed": len(media_urls),
            "images_posted": 0,
            "videos_posted": 0,
            "unsupported_files": len(unsupported),
            "posts_created": [],
            "errors": []
        }
        
        # Post images (Facebook allows multiple images in one post via album)
        if images:
            try:
                # For multiple images, create an album post
                if len(images) == 1:
                    # Single image post
                    params = {
                        "url": images[0],
                        "caption": viral_copyright_text,
                        "published": True
                    }
                    response = self._request("POST", f"{PAGE_ID}/photos", params)
                    if "error" not in response:
                        results["images_posted"] = 1
                        results["posts_created"].append({
                            "type": "image",
                            "media_urls": images,
                            "response": response
                        })
                    else:
                        results["errors"].append({
                            "type": "image",
                            "media_urls": images,
                            "error": response
                        })
                else:
                    # Multiple images - create album
                    # Note: Facebook Graph API album creation is complex, so we'll post images individually
                    for i, image_url in enumerate(images):
                        caption = viral_copyright_text if i == 0 else f"Imagen {i+1} - {content_prompt}"
                        params = {
                            "url": image_url,
                            "caption": caption,
                            "published": True
                        }
                        response = self._request("POST", f"{PAGE_ID}/photos", params)
                        if "error" not in response:
                            results["images_posted"] += 1
                            results["posts_created"].append({
                                "type": "image",
                                "media_url": image_url,
                                "response": response
                            })
                        else:
                            results["errors"].append({
                                "type": "image",
                                "media_url": image_url,
                                "error": response
                            })
            except Exception as e:
                results["errors"].append({
                    "type": "image_processing",
                    "error": str(e)
                })
        
        # Post videos (each video needs its own post)
        for video_url in videos:
            try:
                params = {
                    "source": video_url,
                    "description": viral_copyright_text,
                    "published": True,
                    "content_category": "OTHER"
                }
                response = self._request("POST", f"{PAGE_ID}/videos", params)
                if "error" not in response:
                    results["videos_posted"] += 1
                    results["posts_created"].append({
                        "type": "video",
                        "media_url": video_url,
                        "response": response
                    })
                else:
                    results["errors"].append({
                        "type": "video",
                        "media_url": video_url,
                        "error": response
                    })
            except Exception as e:
                results["errors"].append({
                    "type": "video_processing",
                    "media_url": video_url,
                    "error": str(e)
                })
        
        # Add unsupported files info
        if unsupported:
            results["errors"].append({
                "type": "unsupported_files",
                "files": unsupported,
                "message": "Unsupported file types. Supported: JPG, PNG, GIF, WebP (images), MP4, MOV, AVI, MKV, WebM (videos)"
            })
        
        # Summary
        results["success"] = len(results["posts_created"]) > 0
        results["total_posts_created"] = len(results["posts_created"])
        
        return results
