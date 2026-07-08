"use client";

import { useEffect } from "react";
import { Loader2, ExternalLink } from "lucide-react";
import { profileApi } from "@/shared/api/gateway";
import { ApiError } from "@/shared/api/errors";
import { useProfileStore } from "@/shared/state/profileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { ProfileHeader } from "./ProfileHeader";
import { ExperienceSection } from "./ExperienceSection";
import { EducationSection } from "./EducationSection";
import { SkillsSection } from "./SkillsSection";
import { ProjectsSection } from "./ProjectsSection";
import { CertificationsSection } from "./CertificationsSection";
import { LanguagesSection } from "./LanguagesSection";
import { AchievementsSection } from "./AchievementsSection";
import { SocialLinksSection } from "./SocialLinksSection";
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
      } catch (err: unknown) {
        const status = err instanceof ApiError ? err.status : 0;
        if (status === 404) {
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
      
      {/* Profile Sections */}
      <div className="space-y-6">
        <ExperienceSection experiences={profile.experiences} />
        <EducationSection education={profile.education} />
        <SkillsSection skills={profile.skills} />
        <ProjectsSection projects={profile.projects} />
        <CertificationsSection certifications={profile.certifications} />
        <LanguagesSection languages={profile.languages} />
        <AchievementsSection achievements={profile.achievements} />
        <SocialLinksSection socialLinks={profile.social_links} />
      </div>
    </div>
  );
}
