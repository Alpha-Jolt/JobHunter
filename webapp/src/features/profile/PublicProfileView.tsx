import { UserProfile } from "@/shared/api/types";
import { MapPin, Link as LinkIcon, Briefcase } from "lucide-react";

export function PublicProfileView({ profile }: { profile: UserProfile }) {
  return (
    <div className="max-w-4xl mx-auto py-12 px-4 space-y-12">
      {/* Hero Section */}
      <section className="flex flex-col md:flex-row gap-8 items-center md:items-start text-center md:text-left">
        {profile.avatar_url ? (
          <div className="h-40 w-40 rounded-full overflow-hidden border-4 border-background shadow-lg shrink-0">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={profile.avatar_url} alt={profile.username} className="h-full w-full object-cover" />
          </div>
        ) : (
          <div className="h-40 w-40 rounded-full bg-secondary flex items-center justify-center text-3xl font-bold text-muted-foreground border-4 border-background shadow-lg shrink-0">
            {profile.username.charAt(0).toUpperCase()}
          </div>
        )}
        <div className="space-y-4 pt-2">
          <div>
            <h1 className="text-4xl font-extrabold text-foreground tracking-tight">{profile.username}</h1>
            {profile.headline && <p className="text-xl text-primary font-medium mt-1">{profile.headline}</p>}
          </div>
          <div className="flex flex-wrap gap-4 text-muted-foreground justify-center md:justify-start">
            {profile.location && (
              <div className="flex items-center gap-1.5">
                <MapPin className="h-4 w-4" />
                <span>{profile.location}</span>
              </div>
            )}
            {profile.website_url && (
              <a
                href={profile.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 hover:text-primary transition-colors"
              >
                <LinkIcon className="h-4 w-4" />
                <span>Website</span>
              </a>
            )}
          </div>
        </div>
      </section>

      {/* Bio / Summary */}
      {profile.bio && (
        <section className="bg-card border border-border rounded-xl p-8 shadow-sm">
          <h2 className="text-2xl font-semibold mb-4 text-foreground flex items-center gap-2">
            <Briefcase className="h-5 w-5 text-primary" />
            About Me
          </h2>
          <div className="prose prose-sm md:prose-base dark:prose-invert max-w-none">
            {profile.bio.split("\n").map((line, i) => (
              <p key={i} className="mb-2 last:mb-0 leading-relaxed">
                {line}
              </p>
            ))}
          </div>
        </section>
      )}

      {/* Skills (Optional) */}
      {profile.skills && profile.skills.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-foreground px-2">Skills</h2>
          <div className="flex flex-wrap gap-2 px-2">
            {profile.skills.map((skill) => (
              <span
                key={skill.skill_id}
                className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded-full text-sm font-medium border border-border shadow-sm"
              >
                {skill.name} {skill.proficiency && <span className="opacity-70 ml-1 text-xs">({skill.proficiency})</span>}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Social Links (Optional) */}
      {profile.social_links && profile.social_links.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-foreground px-2">Links</h2>
          <div className="flex flex-wrap gap-4 px-2">
            {profile.social_links.map((link) => (
              <a
                key={link.link_id}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline font-medium"
              >
                {link.platform}
              </a>
            ))}
          </div>
        </section>
      )}

      <footer className="pt-12 pb-8 text-center text-sm text-muted-foreground border-t border-border mt-12">
        Powered by JobHunter
      </footer>
    </div>
  );
}
