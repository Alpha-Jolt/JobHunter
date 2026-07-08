import { notFound } from "next/navigation";
import { PublicProfileView } from "@/features/profile/PublicProfileView";
import { config } from "@/lib/config";
import { UserProfile } from "@/shared/api/types";

interface PageProps {
  params: Promise<{ username: string }>;
}

export async function generateMetadata({ params }: PageProps) {
  const { username } = await params;
  return {
    title: `${username} | JobHunter Profile`,
    description: `View ${username}'s professional profile on JobHunter.`,
  };
}

export default async function PublicProfilePage({ params }: PageProps) {
  const { username } = await params;
  try {
    const res = await fetch(`${config.apiBaseUrl}/api/profile/u/${username}`, {
      next: { revalidate: 60 },
    });
    
    if (!res.ok) {
      if (res.status === 404) return notFound();
      throw new Error(`Failed to fetch profile: ${res.status}`);
    }
    
    const profile: UserProfile = await res.json();
    return <PublicProfileView profile={profile} />;
  } catch (error) {
    console.error("Error fetching public profile:", error);
    return notFound();
  }
}
