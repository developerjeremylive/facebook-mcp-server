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
