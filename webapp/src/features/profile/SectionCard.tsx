import { ReactNode } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/shared/components/Button";

interface SectionCardProps {
  title: string;
  onAdd?: () => void;
  children: ReactNode;
}

export function SectionCard({ title, onAdd, children }: SectionCardProps) {
  return (
    <div className="bg-card border border-border rounded-lg shadow-sm overflow-hidden mb-6">
      <div className="px-6 py-4 border-b border-border flex items-center justify-between">
        <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        {onAdd && (
          <Button variant="ghost" size="sm" onClick={onAdd} className="h-8 gap-1">
            <Plus className="h-4 w-4" /> Add
          </Button>
        )}
      </div>
      <div className="p-6">{children}</div>
    </div>
  );
}
