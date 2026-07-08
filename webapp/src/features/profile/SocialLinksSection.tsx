"use client";

import { useState } from "react";
import { Plus, X, Loader2, Link as LinkIcon, Globe } from "lucide-react";
import { SocialLinkEntry } from "@/shared/api/types";
import { profileApi } from "@/shared/api/gateway";
import { useProfileStore } from "@/shared/state/profileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { SectionCard } from "./SectionCard";
import { Button } from "@/shared/components/Button";
import { Input } from "@/shared/components/Input";

const PLATFORMS = [
  { id: "LinkedIn", icon: Globe },
  { id: "GitHub", icon: Globe },
  { id: "Twitter", icon: Globe },
  { id: "Portfolio", icon: Globe },
  { id: "Other", icon: LinkIcon },
];

export function SocialLinksSection({ socialLinks }: { socialLinks: SocialLinkEntry[] }) {
  const { addToast } = useUiStore();
  const { updateSection } = useProfileStore();
  const [isSaving, setIsSaving] = useState(false);
  
  const [showForm, setShowForm] = useState(false);
  const [newPlatform, setNewPlatform] = useState("LinkedIn");
  const [newUrl, setNewUrl] = useState("");

  const handleAdd = async () => {
    if (!newUrl.trim()) return;

    setIsSaving(true);
    try {
      const newEntry: SocialLinkEntry = {
        link_id: crypto.randomUUID(),
        platform: newPlatform,
        url: newUrl.trim(),
        order_index: socialLinks.length,
      };

      const updatedLinks = [...socialLinks, newEntry];
      
      updateSection({ social_links: updatedLinks });
      
      await profileApi.replaceSocialLinks(updatedLinks.map(l => ({
        platform: l.platform,
        url: l.url,
        order_index: l.order_index
      })));
      
      setNewUrl("");
      setNewPlatform("LinkedIn");
      setShowForm(false);
      addToast("success", "Link added");
    } catch {
      updateSection({ social_links: socialLinks });
      addToast("error", "Failed to add link");
    } finally {
      setIsSaving(false);
    }
  };

  const handleRemove = async (id: string) => {
    setIsSaving(true);
    try {
      const updatedLinks = socialLinks.filter((l) => l.link_id !== id).map((l, idx) => ({ ...l, order_index: idx }));
      
      updateSection({ social_links: updatedLinks });
      
      await profileApi.replaceSocialLinks(updatedLinks.map(l => ({
        platform: l.platform,
        url: l.url,
        order_index: l.order_index
      })));
      
    } catch {
      updateSection({ social_links: socialLinks });
      addToast("error", "Failed to remove link");
    } finally {
      setIsSaving(false);
    }
  };

  const getPlatformIcon = (platform: string) => {
    const found = PLATFORMS.find(p => p.id === platform);
    const Icon = found ? found.icon : LinkIcon;
    return <Icon className="h-4 w-4" />;
  };

  return (
    <SectionCard 
      title="Social Links" 
      onAdd={() => setShowForm(true)}
    >
      <div className="space-y-4">
        {socialLinks.length === 0 && !showForm ? (
          <div className="text-center py-6 text-muted-foreground">
            <LinkIcon className="h-12 w-12 mx-auto mb-3 opacity-20" />
            <p>No social links added yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {socialLinks.map((link) => (
              <div 
                key={link.link_id}
                className="group flex items-center justify-between p-3 border border-border rounded-lg bg-card hover:border-primary/50 transition-colors"
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className="text-muted-foreground">
                    {getPlatformIcon(link.platform)}
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-foreground">{link.platform}</p>
                    <a href={link.url} target="_blank" rel="noopener noreferrer" className="text-xs text-muted-foreground hover:text-primary hover:underline truncate block">
                      {link.url.replace(/^https?:\/\//, '')}
                    </a>
                  </div>
                </div>
                <button
                  onClick={() => handleRemove(link.link_id)}
                  disabled={isSaving}
                  className="p-1.5 rounded-md hover:bg-destructive/10 text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {showForm && (
          <div className="bg-muted/50 p-4 rounded-lg border border-border space-y-3 mt-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                value={newPlatform}
                onChange={(e) => setNewPlatform(e.target.value)}
              >
                {PLATFORMS.map(p => (
                  <option key={p.id} value={p.id}>{p.id}</option>
                ))}
              </select>
              <div className="md:col-span-2">
                <Input
                  placeholder="https://..."
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleAdd();
                    if (e.key === "Escape") setShowForm(false);
                  }}
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button size="sm" onClick={handleAdd} disabled={isSaving || !newUrl.trim()}>
                {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Plus className="mr-2 h-4 w-4" />}
                Add Link
              </Button>
            </div>
          </div>
        )}
      </div>
    </SectionCard>
  );
}
