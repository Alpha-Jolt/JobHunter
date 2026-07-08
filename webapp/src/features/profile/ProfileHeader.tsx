"use client";

import { useState } from "react";
import { UserProfile } from "@/shared/api/types";
import { profileApi } from "@/shared/api/gateway";
import { useUiStore } from "@/shared/state/uiStore";
import { useProfileStore } from "@/shared/state/profileStore";
import { SectionCard } from "./SectionCard";
import { Button } from "@/shared/components/Button";
import { Input } from "@/shared/components/Input";
import { Camera, Loader2 } from "lucide-react";

export function ProfileHeader({ profile }: { profile: UserProfile }) {
  const { addToast } = useUiStore();
  const { updateSection } = useProfileStore();
  const [isUploading, setIsUploading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    username: profile.username || "",
    headline: profile.headline || "",
    bio: profile.bio || "",
    location: profile.location || "",
    website_url: profile.website_url || "",
    is_public: profile.is_public || false,
  });

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      addToast("error", "Avatar must be less than 5MB");
      return;
    }

    setIsUploading(true);
    try {
      const res = await profileApi.uploadAvatar(file);
      updateSection({ avatar_url: res.avatar_url });
      addToast("success", "Avatar updated successfully");
    } catch {
      addToast("error", "Failed to upload avatar");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updated = await profileApi.updateMe(formData);
      updateSection(updated);
      addToast("success", "Profile overview saved");
    } catch {
      addToast("error", "Failed to save profile");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <SectionCard title="Overview">
      <div className="flex flex-col md:flex-row gap-8">
        <div className="flex flex-col items-center gap-4">
          <div className="relative h-32 w-32 rounded-full overflow-hidden bg-muted border-4 border-background shadow-sm">
            {profile.avatar_url ? (
              <>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={profile.avatar_url} alt="Avatar" className="h-full w-full object-cover" />
              </>
            ) : (
              <div className="h-full w-full flex items-center justify-center text-muted-foreground bg-secondary">
                No Avatar
              </div>
            )}
            <label className="absolute inset-0 bg-black/40 flex flex-col items-center justify-center text-white opacity-0 hover:opacity-100 cursor-pointer transition-opacity">
              {isUploading ? <Loader2 className="h-6 w-6 animate-spin" /> : <Camera className="h-6 w-6" />}
              <span className="text-xs mt-1 text-center font-medium">Change<br/>Avatar</span>
              <input type="file" className="hidden" accept="image/jpeg,image/png,image/webp" onChange={handleAvatarUpload} disabled={isUploading} />
            </label>
          </div>
          <label className="flex items-center gap-2 text-sm font-medium cursor-pointer">
            <input
              type="checkbox"
              checked={formData.is_public}
              onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
              className="rounded border-input text-primary focus:ring-primary"
            />
            Publish Profile
          </label>
        </div>

        <div className="flex-1 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-medium text-foreground">Username</label>
              <Input
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                placeholder="Unique username"
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-foreground">Location</label>
              <Input
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                placeholder="e.g. San Francisco, CA"
              />
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Headline</label>
            <Input
              value={formData.headline}
              onChange={(e) => setFormData({ ...formData, headline: e.target.value })}
              placeholder="e.g. Senior Software Engineer"
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Website URL</label>
            <Input
              type="url"
              value={formData.website_url}
              onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
              placeholder="https://yourwebsite.com"
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground">Bio / Summary</label>
            <textarea
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              placeholder="Tell us about your background and goals..."
              className="flex min-h-[120px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
          <div className="flex justify-end pt-2">
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Save Overview
            </Button>
          </div>
        </div>
      </div>
    </SectionCard>
  );
}
