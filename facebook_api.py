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
