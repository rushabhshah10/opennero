#ifndef _OPENNERO_AI_RTNEAT_SCOREHELPER_H_
#define _OPENNERO_AI_RTNEAT_SCOREHELPER_H_

#include "core/Preprocessor.h"
#include "ai/AI.h"

namespace OpenNero
{
    using namespace std;


    /// Holdings scoring information
    class ScoreHelper {
    private:

        size_t m_SampleSize;
        Reward m_Zero;
        Reward m_Total;
        Reward m_SumOfSquares;
        Reward m_Average;
        Reward m_StandardDeviation;

    public:
    
        ScoreHelper(const RewardInfo& zero);
        ~ScoreHelper();

        void reset();
        void doCalculations();
        void calculateAverages();
        void calculateStandardDeviations();

        /// add a reward sample
        inline void addSample(Reward sample);

        /// preferred generic method
        inline Reward getAverage();

        /// preferred generic method
        inline Reward getRelativeScore(Reward absoluteScore);
    };
    
    class Stats
    {
    public:
        static U32 s_RunningAverageSampleSize;
    private:
        
        /// Number of trials processed over the unit's lifetime
        U32 m_NumLifetimeTrials;
        
        /// Zero stats (for resetting)
        Reward m_ZeroStats;
        
        /// Fields for holding stat accumulations
        Reward m_Stats;
        
        /// Lifetime averages of stat accumulations
        Reward m_LifetimeAverage;
        
    public:
        /// Constructor
        explicit Stats(const RewardInfo& info);
        
        /// Destructor
        ~Stats() {}
        
        /// Reset all stats
        void resetAll();
        
        /// start next trial
        void startNextTrial();
        
        /// predict what stats would be w/o death
        void predictStats(int timeAlive, int fullLife );
        
        // Stat-tallying methods
        void tally(Reward sample);
        
        /// Stat-retrieval methods
        inline Reward getStats();
    };    
}

#endif // _OPENNERO_AI_RTNEAT_SCOREHELPER_H_