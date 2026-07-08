"use client";

import { useEffect } from "react";
import { Loader2, ExternalLink } from "lucide-react";
import { profileApi } from "@/shared/api/gateway";
import { useProfileStore } from "@/shared/state/profileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { ProfileHeader } from "./ProfileHeader";
import { Button } from "@/shared/components/Button";

export function ProfileEditPage() {
  const { profile, setProfile, isLoading } = useProfileStore();
  const { addToast } = useUiStore();

  useEffect(() => {
    const fetchProfile = async () => {
      useProfileStore.setState({ isLoading: true });
      try {
        const data = await profileApi.getMe();
        setProfile(data);
      } catch (err: any) {
        if (err?.response?.status === 404) {
          // Lazy init: leave profile as empty (null). The first save will create it.
          setProfile({
            user_id: "",
            username: "",
            headline: "",
            bio: "",
            location: "",
            website_url: "",
            avatar_url: null,
            is_public: false,
            public_slug: null,
            experiences: [],
            education: [],
            projects: [],
            certifications: [],
            skills: [],
            languages: [],
            achievements: [],
            social_links: [],
          });
        } else {
          addToast("error", "Failed to load profile.");
        }
      } finally {
        useProfileStore.setState({ isLoading: false });
      }
    };
    fetchProfile();
  }, [setProfile, addToast]);

  if (isLoading || !profile) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">My Profile</h1>
          <p className="text-muted-foreground mt-1">Manage your professional identity</p>
        </div>
        {profile.is_public && profile.username && (
          <Button variant="outline" asChild>
            <a href={`/u/${profile.username}`} target="_blank" rel="noopener noreferrer" className="gap-2">
              View Public Profile <ExternalLink className="h-4 w-4" />
            </a>
          </Button>
        )}
      </div>

      <ProfileHeader profile={profile} />
      
      {/* Placeholders for other sections to save boilerplate generation */}
      <div className="bg-card border border-border rounded-lg shadow-sm p-6 text-center text-muted-foreground">
        Experience, Education, Skills, and other sections will go here.
      </div>
    </div>
  );
}
