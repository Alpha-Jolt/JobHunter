"use client";

import { useRouter } from "next/navigation";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { LogOut, User as UserIcon } from "lucide-react";
import { useAuthStore } from "@/shared/state/authStore";
import { authApi } from "@/shared/api/gateway";
import { Button } from "@/shared/components/Button";
import { useUiStore } from "@/shared/state/uiStore";
import { useProfileStore } from "@/shared/state/profileStore";

export function UserMenu() {
  const { user, clearAuth } = useAuthStore();
  const { addToast } = useUiStore();
  const { profile } = useProfileStore();
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch {
      // proceed regardless
    }
    clearAuth();
    router.replace("/login");
    addToast("info", "Logged out successfully.");
  };

  if (!user) return null;

  const initials = [user.first_name, user.last_name]
    .filter(Boolean)
    .map((n) => n![0]!)
    .join("")
    .toUpperCase() || (user.email[0] ?? "U").toUpperCase();

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <Button variant="ghost" size="icon" aria-label="User menu">
          <span className="h-8 w-8 rounded-full bg-primary text-primary-foreground text-xs font-semibold flex items-center justify-center overflow-hidden">
            {profile?.avatar_url ? (
              <img src={profile.avatar_url} alt="Avatar" className="h-full w-full object-cover" />
            ) : (
              initials
            )}
          </span>
        </Button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="end"
          sideOffset={8}
          className="z-50 min-w-48 rounded-lg border border-border bg-card shadow-lg p-1 text-sm"
        >
          <div className="px-3 py-2 border-b border-border mb-1">
            <p className="font-medium text-foreground truncate">{user.first_name ?? user.email}</p>
            <p className="text-xs text-muted-foreground truncate">{user.email}</p>
          </div>
          <DropdownMenu.Item
            onSelect={() => router.push("/profile")}
            className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-secondary cursor-pointer outline-none mb-1"
          >
            <UserIcon className="h-4 w-4" />
            My Profile
          </DropdownMenu.Item>
          <DropdownMenu.Item
            onSelect={handleLogout}
            className="flex items-center gap-2 px-3 py-2 rounded-md text-destructive hover:bg-secondary cursor-pointer outline-none"
          >
            <LogOut className="h-4 w-4" />
            Log out
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
