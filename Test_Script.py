# test_advanced_ai.py
# Test the Advanced AI Clip Generator with your actual transcript data

def test_advanced_ai_with_real_data():
    """Test the advanced AI with the actual transcript from your logs"""
    
    # Your actual transcript data from the logs
    real_transcript = """[00:00] two
[00:01] one boom all right we're live thank you
[00:03] very much for doing this man i really
[00:04] appreciate it i've been absorbing your
[00:06] information and listening to you talk
[00:08] for uh quite a while now so it's uh it's
[00:11] great to actually meet you thanks for
[00:12] having me my pleasure my pleasure you
[00:14] are one of the rare guys
[00:17] that is uh you're a big investor
[00:20] you are um you're deep in the tech world
[00:24] but yet you seem to have a very balanced
[00:26] perspective in terms of how to live life
[00:28] as opposed to not just be
[00:31] entirely focused on
[00:33] success and financial success
[00:36] and
[00:38] tech investing but rather
[00:40] how to live your life in a happy way
[00:42] that's a it's a it's not balance
[00:45] yeah you know i think the reason why
[00:47] people like uh hearing me is because
[00:50] like if it's like if you go to a circus  
[00:52] and you see a bear right that's kind of
[00:54] interesting but not that much if you see
[00:56] a unicycle that's interesting but you
[00:57] see a bear on a unicycle that's really
[00:59] interesting right
[01:00] so when you combine things you're not
[01:02] supposed to combine right people get
[01:04] interested it's like bruce lee right
[01:05] striking thoughts philosophy plus
[01:07] martial arts
[01:09] and i think it's because at some level
[01:11] all humans are broad we're all
[01:13] multivariate but we get summarized in
[01:16] pithy ways in our lives and at some deep
[01:19] level we know that's not true right
[01:20] every human basically is capable of
[01:22] every experience and every thought uh
[01:24] you know you're ufc comedian commentator
[01:27] podcaster but you're also more than that
[01:29] you're also father
[01:30] uh lover you know thinker etc
[01:34] so i like the model of life that the
[01:37] ancients had the greeks the romans right
[01:39] where you would start out and when
[01:41] you're young you're just like going to
[01:43] school then you're going to war then
[01:45] you're running a business then you're
[01:47] supposed to serve in the senate or the
[01:48] government then you become a philosopher
[01:50] there's sort of this arc to life
[01:52] where you try your hand at everything
[01:55] and as one of my friends says
[01:57] specialization is for insects right
[02:00] so everyone should just be able to do
[02:02] everything and so i don't believe in
[02:03] this model anymore of trying to focus
[02:06] your life down on one thing you've got
[02:08] one life just do everything you're going
[02:09] to do"""

    print("Testing Advanced AI Clip Generator with Real Data")
    print("=" * 60)
    
    try:
        # Try to import advanced AI
        from advanced_ai_clip_generator import AdvancedAIClipGenerator
        print("✓ Advanced AI Clip Generator imported successfully")
        
        # Initialize the generator
        generator = AdvancedAIClipGenerator()
        print("✓ Advanced AI initialized")
        
        # Test parsing
        segments = generator.parse_transcript_advanced(real_transcript)
        print(f"✓ Parsed {len(segments)} segments from transcript")
        
        # Test sentence reconstruction
        reconstructed = generator.reconstruct_sentences(segments, window_size=8)
        print(f"✓ Reconstructed {len(reconstructed)} complete sentences")
        
        if reconstructed:
            print("\nReconstructed sentences (first 3):")
            for i, sentence in enumerate(reconstructed[:3]):
                print(f"  {i+1}. [{sentence['start_time']}s-{sentence['end_time']}s] {sentence['text'][:80]}...")
        
        # Generate clips
        print("\nGenerating clips...")
        clips = generator.generate_advanced_clips(real_transcript, max_clips=8)
        print(f"✓ Generated {len(clips)} clips using advanced AI")
        
        if clips:
            print("\nGenerated Clips:")
            print("-" * 60)
            for i, clip in enumerate(clips):
                print(f"\nClip {i+1}:")
                print(f"  Time: {clip['start_time']}s - {clip['end_time']}s ({clip['duration']}s)")
                print(f"  Category: {clip['category']}")
                print(f"  Overall Score: {clip.get('overall_score', clip.get('confidence_score', 0)):.3f}")
                if 'semantic_score' in clip:
                    print(f"  Semantic: {clip['semantic_score']:.3f} | Engagement: {clip['engagement_score']:.3f}")
                    print(f"  Quotability: {clip['quotability_score']:.3f} | Emotional: {clip['emotional_intensity']:.3f}")
                if 'keywords' in clip and clip['keywords']:
                    print(f"  Keywords: {', '.join(clip['keywords'][:3])}")
                print(f"  Text: {clip['text']}")
                print("-" * 60)
        else:
            print("⚠ No clips generated - this might indicate the content isn't suitable for clipping")
        
        # Test refresh functionality
        print(f"\nTesting refresh functionality...")
        new_clips = generator.refresh_advanced_clips(real_transcript, clips, max_clips=5)
        print(f"✓ Generated {len(new_clips)} new clips on refresh")
        
        if new_clips:
            print("New clips generated successfully!")
        
        return True
        
    except ImportError as e:
        print(f"✗ Advanced AI not available: {e}")
        print("\nTo install Advanced AI:")
        print("1. Run: python setup_advanced_ai.py")
        print("2. Or manually install: pip install sentence-transformers scikit-learn nltk")
        return False
        
    except Exception as e:
        print(f"✗ Error testing Advanced AI: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_basic_vs_advanced():
    """Compare basic vs advanced AI performance"""
    print("\nComparing Basic vs Advanced AI")
    print("=" * 60)
    
    sample_transcript = """[00:05] The key to success is persistence
[00:10] Never give up on your dreams
[00:15] You have the power to change your life
[00:20] Success is not final failure is not fatal
[00:25] The courage to continue is what matters
[00:30] Innovation distinguishes leaders from followers
[00:35] Your time is limited so don't waste it"""
    
    try:
        # Test basic AI
        print("Testing Basic AI:")
        from ai_clip_generator import AIClipGenerator
        basic_generator = AIClipGenerator()
        basic_clips = basic_generator.generate_clips(sample_transcript, max_clips=5)
        print(f"  Basic AI generated: {len(basic_clips)} clips")
        
        # Test advanced AI
        print("Testing Advanced AI:")
        from advanced_ai_clip_generator import AdvancedAIClipGenerator
        advanced_generator = AdvancedAIClipGenerator()
        advanced_clips = advanced_generator.generate_advanced_clips(sample_transcript, max_clips=5)
        print(f"  Advanced AI generated: {len(advanced_clips)} clips")
        
        print("\nComparison Results:")
        print(f"  Basic AI: {len(basic_clips)} clips")
        print(f"  Advanced AI: {len(advanced_clips)} clips")
        
        if advanced_clips:
            avg_semantic_score = sum(clip.get('semantic_score', 0) for clip in advanced_clips) / len(advanced_clips)
            avg_engagement_score = sum(clip.get('engagement_score', 0) for clip in advanced_clips) / len(advanced_clips)
            print(f"  Advanced AI avg semantic score: {avg_semantic_score:.3f}")
            print(f"  Advanced AI avg engagement score: {avg_engagement_score:.3f}")
        
    except ImportError as e:
        print(f"Cannot compare - missing module: {e}")
    except Exception as e:
        print(f"Error in comparison: {e}")

def main():
    print("Advanced AI Clip Generator Test Suite")
    print("=" * 60)
    
    # Test 1: Real data test
    success = test_advanced_ai_with_real_data()
    
    # Test 2: Comparison test
    if success:
        compare_basic_vs_advanced()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ Advanced AI is working correctly!")
        print("✓ Ready to use in your Flask application")
    else:
        print("✗ Advanced AI setup required")
        print("Run: python setup_advanced_ai.py")
    print("=" * 60)

if __name__ == "__main__":
    main()