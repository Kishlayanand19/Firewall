import { SocialFeed } from "@/components/feed/SocialFeed";

export default function FeedPage() {
  return (
    <div className="px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold gradient-text">Feed Simulation</h1>
        <p className="text-slate-400 mt-1">Browser-like social media feed with threat highlighting</p>
      </div>
      <SocialFeed />
    </div>
  );
}
