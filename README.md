// GenerateGamePackageEditor.cs
// Place this file in Assets/Editor/ then open Unity and use Tools -> Generate Game .unitypackage
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

public class GenerateGamePackageEditor : EditorWindow
{
    const string targetFolder = "Assets/GeneratedGamePackage";
    [MenuItem("Tools/Generate Game .unitypackage")]
    public static void ShowWindow()
    {
        var w = GetWindow<GenerateGamePackageEditor>("Generate Game Package");
        w.minSize = new Vector2(480, 220);
    }

    void OnGUI()
    {
        GUILayout.Label("Generate and Export Game Scripts Package", EditorStyles.boldLabel);
        GUILayout.Space(6);
        EditorGUILayout.HelpBox("This tool will create a folder 'Assets/GeneratedGamePackage' with all scripts, refresh the AssetDatabase, and export it as a .unitypackage.\n\nIf the folder already exists, files inside will be overwritten.", MessageType.Info);
        GUILayout.Space(6);

        if (GUILayout.Button("Generate & Export Package", GUILayout.Height(40)))
        {
            if (EditorUtility.DisplayDialog("Generate & Export", "This will create/overwrite files in " + targetFolder + ". Continue?", "Yes", "Cancel"))
            {
                GenerateAndExport();
            }
        }

        GUILayout.FlexibleSpace();

        if (GUILayout.Button("Open Generated Folder in Project (if exists)"))
        {
            var obj = AssetDatabase.LoadAssetAtPath<Object>(targetFolder);
            if (obj != null) Selection.activeObject = obj;
            else EditorUtility.DisplayDialog("Open Folder", "Folder does not exist yet. Generate package first.", "OK");
        }
    }

    void GenerateAndExport()
    {
        try
        {
            CreateFiles();
            AssetDatabase.Refresh();

            string defaultName = "GeneratedGameScripts.unitypackage";
            string path = EditorUtility.SaveFilePanel("Save .unitypackage", "", defaultName, "unitypackage");
            if (string.IsNullOrEmpty(path))
            {
                Debug.Log("Export cancelled.");
                return;
            }

            // Export the generated folder recursively
            EditorUtility.DisplayProgressBar("Exporting", "Exporting package...", 0.8f);
            AssetDatabase.ExportPackage(new string[] { targetFolder }, path, ExportPackageOptions.Recurse);
            EditorUtility.ClearProgressBar();

            EditorUtility.DisplayDialog("Export Complete", "Exported package to:\n" + path, "OK");
            Debug.Log("Exported package to: " + path);
        }
        catch (System.Exception ex)
        {
            Debug.LogError("Error generating/exporting package: " + ex);
            EditorUtility.ClearProgressBar();
        }
    }

    void CreateFiles()
    {
        // Ensure directory
        string scriptsPath = Path.Combine(targetFolder, "Scripts");
        if (!Directory.Exists(scriptsPath)) Directory.CreateDirectory(scriptsPath);

        // Dictionary filename -> contents
        var files = new Dictionary<string, string>()
        {
            // CaptureDeviceType.cs
            ["Scripts/CaptureDeviceType.cs"] = @"public enum CaptureDeviceType
{
    BasicBall,
    GreatBall,
    UltraBall,
    MasterBall
}
",

            // InventoryManager.cs
            ["Scripts/InventoryManager.cs"] = @"using System.Collections.Generic;
using UnityEngine;

[DisallowMultipleComponent]
public class InventoryManager : MonoBehaviour
{
    public static InventoryManager Instance;

    // Internal storage
    private Dictionary<CaptureDeviceType, int> deviceCounts = new Dictionary<CaptureDeviceType, int>();

    void Awake()
    {
        if (Instance == null) Instance = this;
        else { Destroy(gameObject); return; }

        DontDestroyOnLoad(gameObject);
        EnsureDefaults();
    }

    void EnsureDefaults()
    {
        if (!deviceCounts.ContainsKey(CaptureDeviceType.BasicBall)) deviceCounts[CaptureDeviceType.BasicBall] = 10;
        if (!deviceCounts.ContainsKey(CaptureDeviceType.GreatBall)) deviceCounts[CaptureDeviceType.GreatBall] = 3;
        if (!deviceCounts.ContainsKey(CaptureDeviceType.UltraBall)) deviceCounts[CaptureDeviceType.UltraBall] = 1;
        if (!deviceCounts.ContainsKey(CaptureDeviceType.MasterBall)) deviceCounts[CaptureDeviceType.MasterBall] = 0;
    }

    public int GetCount(CaptureDeviceType type)
    {
        if (deviceCounts.TryGetValue(type, out int c)) return c;
        return 0;
    }

    public void AddDevice(CaptureDeviceType type, int amount)
    {
        if (!deviceCounts.ContainsKey(type)) deviceCounts[type] = 0;
        deviceCounts[type] += amount;
    }

    public bool UseDevice(CaptureDeviceType type)
    {
        if (!deviceCounts.ContainsKey(type)) return false;
        if (deviceCounts[type] <= 0) return false;
        deviceCounts[type]--;
        return true;
    }

    public DeviceSaveData[] GetSaveArray()
    {
        var list = new List<DeviceSaveData>();
        foreach (CaptureDeviceType t in System.Enum.GetValues(typeof(CaptureDeviceType)))
        {
            list.Add(new DeviceSaveData { deviceType = t, count = GetCount(t) });
        }
        return list.ToArray();
    }

    public void LoadFromSave(DeviceSaveData[] arr)
    {
        deviceCounts.Clear();
        if (arr == null) { EnsureDefaults(); return; }
        foreach (var d in arr)
        {
            deviceCounts[d.deviceType] = d.count;
        }
        EnsureDefaults();
    }
}

[System.Serializable]
public struct DeviceSaveData
{
    public CaptureDeviceType deviceType;
    public int count;
}
",

            // CreatureData.cs
            ["Scripts/CreatureData.cs"] = @"using System;

[Serializable]
public class CreatureData
{
    public string creatureName;
    public Element element;
    public int level;
    public int maxHP;
    public int currentHP;
    public int attack;
    public int defense;
    public Ability[] abilities;
    public int xpReward;

    // rarity & captured flag
    public Rarity rarity = Rarity.Common;
    public bool isCaptured = false;

    // protected flag (for Sanctuary)
    public bool isProtected = false;

    // evolution state
    public bool isEvolved = false;
    public int evolutionStage = 0;
    public int nextEvolutionLevel = -1;
}
",

            // Creature.cs
            ["Scripts/Creature.cs"] = @"using UnityEngine;

public class Creature : MonoBehaviour
{
    [Header(""Identity"")]
    public string creatureName = ""Wild Creature"";
    public Element element = Element.Neutral;
    public Rarity rarity = Rarity.Common;

    [Header(""Stats"")]
    public int level = 1;
    public int maxHP = 50;
    public int currentHP = 50;
    public int attack = 10;
    public int defense = 5;
    public int xpReward = 20;

    [Header(""Abilities"")]
    public Ability[] abilities;

    [Header(""Battle settings"")]
    public bool isWild = true;

    [Header(""Evolution"")]
    public bool isEvolved = false;
    public int evolutionStage = 0;
    public int nextEvolutionLevel = -1;

    private void Reset()
    {
        abilities = new Ability[] {
            new Ability(""Strike"", Element.Neutral, 10),
            new Ability(""Elemental Burst"", element, 12)
        };
        rarity = Rarity.Common;
    }

    private void Start()
    {
        currentHP = Mathf.Clamp(currentHP, 1, maxHP);
    }

    public CreatureData ToData()
    {
        return new CreatureData
        {
            creatureName = creatureName,
            element = element,
            level = level,
            maxHP = maxHP,
            currentHP = currentHP,
            attack = attack,
            defense = defense,
            abilities = abilities,
            xpReward = xpReward,
            rarity = rarity,
            isCaptured = !isWild,
            isProtected = false,
            isEvolved = isEvolved,
            evolutionStage = evolutionStage,
            nextEvolutionLevel = nextEvolutionLevel
        };
    }

    public int ApplyDamage(int damage)
    {
        int dmg = Mathf.Max(1, damage - defense);
        currentHP -= dmg;
        return dmg;
    }
}
",

            // Element.cs
            ["Scripts/Element.cs"] = @"public enum Element
{
    Fire,
    Water,
    Earth,
    Air,
    Neutral,

    // 20 new elements added below:
    Ice,
    Lightning,
    Poison,
    Psychic,
    Metal,
    Wood,
    Light,
    Dark,
    Sound,
    Gravity,
    Time,
    Space,
    Plasma,
    Crystal,
    Arcane,
    Spirit,
    Steam,
    Sand,
    Magnetic,
    Ethereal
}
",

            // Rarity.cs
            ["Scripts/Rarity.cs"] = @"public enum Rarity
{
    Common = 0,
    Uncommon = 1,
    Rare = 2,
    Epic = 3,
    Legendary = 4
}
",

            // Ability.cs
            ["Scripts/Ability.cs"] = @"using System;

[Serializable]
public class Ability
{
    public string abilityName;
    public Element element;
    public int power;

    public Ability() { abilityName = ""Strike""; element = Element.Neutral; power = 8; }
    public Ability(string name, Element e, int p) { abilityName = name; element = e; power = p; }
}
",

            // ElementalChart.cs
            ["Scripts/ElementalChart.cs"] = @"public static class ElementalChart
{
    // Very simple placeholder effectiveness chart. Return multipliers like 0.5, 1, 2 etc.
    public static float GetEffectiveness(Element attacker, Element defender)
    {
        if (attacker == defender) return 1f;
        // some simple rules
        if (attacker == Element.Fire && defender == Element.Ice) return 2f;
        if (attacker == Element.Water && defender == Element.Fire) return 2f;
        if (attacker == Element.Earth && defender == Element.Lightning) return 2f;
        if (attacker == Element.Light && defender == Element.Dark) return 2f;
        return 1f;
    }
}
",

            // CreatureNamer.cs (large)
            ["Scripts/CreatureNamer.cs"] = @"using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Generates readable creature names that correspond to their Element and reflect rarities.
/// Each element has a base pool (15 names). Rare/epic/legendary/evolved pools are smaller and used by rarity or evolution.
/// Use CreatureNamer.GetName(element, rarity) for base names and CreatureNamer.GetEvolvedName(...) for evolved forms.
/// </summary>
public static class CreatureNamer
{
    // Base name pools per element (≈15 names each)
    static readonly Dictionary<Element, string[]> baseNames = new Dictionary<Element, string[]>
    {
        { Element.Fire, new string[] {
            ""Emberling"",""Cinderfox"",""Blazewing"",""Pyron"",""Ashpup"",""Flareonix"",""Searling"",""Ignis"",""Coalback"",""Singeclaw"",
            ""Kindletail"",""Scorchbat"",""Fumebloss"",""Sparket"",""Torchmite""
        }},

        { Element.Water, new string[] {
            ""Tidekin"",""Aquafin"",""Splashling"",""Ripplon"",""Marinaut"",""Droplet"",""Curran"",""Brinebeak"",""Puddletooth"",""Gulllet"",
            ""Rillscale"",""Surflet"",""Mistfin"",""Torrider"",""Lagoonet""
        }},

        { Element.Earth, new string[] {
            ""Boulderox"",""Terran"",""Rootling"",""Stonehide"",""Gravelot"",""Mossback"",""Gaiaclaw"",""Clodbeast"",""Pebblepup"",""Cragtooth"",
            ""Humusaur"",""Claybrow"",""Mirehorn"",""Quarral"",""Bedrocker""
        }},

        { Element.Air, new string[] {
            ""Zephyra"",""Gustwing"",""Breezlet"",""Aeral"",""Skylark"",""Whisperm"",""Cirrus"",""Galeon"",""Updrafta"",""Cloudlet"",
            ""Aerling"",""Windlet"",""Sirocco"",""Mistral"",""Soarer""
        }},

        { Element.Neutral, new string[] {
            ""Wisp"",""Shade"",""Fawnling"",""Mote"",""Drift"",""Patch"",""Pip"",""Murmur"",""Dapple"",""Glim"",
            ""Nimblet"",""Blanket"",""Quietkin"",""Veillet"",""Smolder""
        }},

        // NEW ELEMENTS (20) - each has ~15 names
        { Element.Ice, new string[] {
            ""Frostlet"",""Glacierpup"",""Shardling"",""Chillfin"",""Hailback"",""Crystalfur"",""Icerift"",""Snowbud"",""Frostreed"",""Glacian"",
            ""Rimeclaw"",""Sleetlet"",""Permafawn"",""Brumal"",""Frigette""
        }},

        { Element.Lightning, new string[] {
            ""Sparklet"",""Voltwing"",""Thunderpup"",""Arcstrike"",""Zapper"",""Stormchip"",""Flashling"",""Chargon"",""Electra"",""Boltail"",
            ""Surgekin"",""Ampereon"",""Stormlet"",""Thundra"",""Pulser""
        }},

        { Element.Poison, new string[] {
            ""Venomoth"",""Toxitail"",""Viperkin"",""Blightclaw"",""Ichorling"",""Slinkven"",""Noxpup"",""Fetidbud"",""Mirevenom"",""Creepseed"",
            ""Rotmist"",""Pestling"",""Corroder"",""Gloomspit"",""Foullet""
        }},

        { Element.Psychic, new string[] {
            ""Mindling"",""Scryer"",""Psybud"",""Dreampup"",""Thoughtlet"",""Eidolon"",""Seerkin"",""Noetica"",""Cerebell"",""Auran"",
            ""Psychette"",""Intuita"",""Wispmind"",""Gleamthought"",""Echoeye""
        }},

        { Element.Metal, new string[] {
            ""Forgeling"",""Ironpup"",""Steelback"",""Alloykin"",""Rustlet"",""Gearmite"",""Plating"",""Brasslet"",""Cobaltet"",""Metallon"",
            ""Smelter"",""Clanglet"",""Boltron"",""Ferretal"",""Magmite""
        }},

        { Element.Wood, new string[] {
            ""Sapling"",""Barkling"",""Twiglet"",""Leafbeast"",""Rootbud"",""Bramblepup"",""Woodkin"",""Silvamite"",""Grovelet"",""Acornox"",
            ""Thornlet"",""Barkpaw"",""Verdant"",""Lignum"",""Spriglet""
        }},

        { Element.Light, new string[] {
            ""Lumina"",""Gleamling"",""Radiant"",""Sunling"",""Lumenpup"",""Glowet"",""Beaconet"",""Sollet"",""Dawning"",""Brill"",
            ""Aurorae"",""Lucent"",""Glister"",""Shinelit"",""Haloet""
        }},

        { Element.Dark, new string[] {
            ""Umbra"",""Shadeclaw"",""Nightpup"",""Gloomling"",""Ebonet"",""Murkwisp"",""Nocturn"",""Duskrift"",""Teneb"",""Sablet"",
            ""Obscura"",""Candlee"",""Nightra"",""Umbralet"",""Shadowin""
        }},

        { Element.Sound, new string[] {
            ""Echolet"",""Tonet"",""Vibrato"",""Chordling"",""Cacklewing"",""Humlet"",""Rumblepup"",""Whistler"",""Sonicet"",""Bellkin"",
            ""Chimebud"",""Reverb"",""Cadence"",""Melodet"",""Fipple""
        }},

        { Element.Gravity, new string[] {
            ""Gravlet"",""Weightpaw"",""Puller"",""Gloomcore"",""Sinker"",""Stonepress"",""Orbital"",""Anchore"",""Pressor"",""Densekin"",
            ""Lodestone"",""Glyth"",""Masslet"",""Tetheron"",""Faller""
        }},

        { Element.Time, new string[] {
            ""Tickling"",""Hourlet"",""Epocha"",""Chronon"",""Pendlet"",""Agetide"",""Momentox"",""Sandsprite"",""Tempus"",""Erafox"",
            ""Clocket"",""Diurnal"",""Timeling"",""Retrolet"",""Latera""
        }},

        { Element.Space, new string[] {
            ""Cosmowisp"",""Stellar"",""Nebulet"",""Voidpup"",""Galaxion"",""Orbitlet"",""Quasarling"",""Astrote"",""Cometkin"",""Lunet"",
            ""Spaceling"",""Celestral"",""Astron"",""Polaris"",""Vortexa""
        }},

        { Element.Plasma, new string[] {
            ""Plasmet"",""Ionling"",""Flarion"",""Ablaze"",""Aurorate"",""Ionette"",""Plasmite"",""Glowcore"",""Fluxlet"",""Coronae"",
            ""Plazma"",""Chargon"",""Filament"",""Aurion"",""Radiantor""
        }},

        { Element.Crystal, new string[] {
            ""Facetkin"",""Gemlet"",""Prismapup"",""Shardling"",""Facetpaw"",""Luminite"",""Gleamcrust"",""Quartzet"",""Sparlet"",""Glimmer"",
            ""Crystelle"",""Beryllet"",""Opaline"",""Facetaur"",""Shinelace""
        }},

        { Element.Arcane, new string[] {
            ""Runeling"",""Glyphlet"",""Sigilon"",""Mystkin"",""Arcanet"",""Wyrdling"",""Hexlet"",""Runewisp"",""Sorcel"",""Charmet"",
            ""Eldra"",""Mystlet"",""Occultor"",""Runefox"",""Spellit""
        }},

        { Element.Spirit, new string[] {
            ""Spectlet"",""Wraithling"",""Phantomkin"",""Spooket"",""Soullet"",""Ethereal"",""Hauntling"",""Ghostet"",""Feypaw"",""Eidol"",
            ""Murmurine"",""Spiritus"",""Shadekin"",""Seance"",""Wispborn""
        }},

        { Element.Steam, new string[] {
            ""Vaporlet"",""Boilet"",""Steamkin"",""Sizzle"",""Mistcoil"",""Geyserpup"",""Pufflet"",""Scaldet"",""Hissling"",""Searmist"",
            ""Thermet"",""Whistlefume"",""Cloudcoil"",""Vaporeonix"",""Condensa""
        }},

        { Element.Sand, new string[] {
            ""Duneling"",""Grainpaw"",""Siltlet"",""Dunebeast"",""Quickshet"",""Sandtail"",""Gritlet"",""Duneborn"",""Siroccet"",""Sandaroo"",
            ""Miraget"",""Oaslet"",""Duster"",""Sandyx"",""Bedou""
        }},

        { Element.Magnetic, new string[] {
            ""Magneto"",""Pollet"",""Fluxpaw"",""Attractor"",""Repulset"",""Lorent"",""Coilent"",""Polatron"",""Maglet"",""Ferrin"",
            ""Fieldling"",""Magnetide"",""Dipole"",""Barlet"",""Electrocoil""
        }},

        { Element.Ethereal, new string[] {
            ""Aetherling"",""Lumenghost"",""Veilkin"",""Gossamer"",""Sylphlet"",""Silvanth"",""Nebulon"",""Auralis"",""Faintpaw"",""Glimmerwisp"",
            ""Subtile"",""Lacuna"",""Whispere"",""Echolite"",""Netheret""
        }}
    };

    // Special nicer names for higher rarities per element (smaller pools)
    static readonly Dictionary<Element, string[]> rareNames = new Dictionary<Element, string[]>
    {
        { Element.Fire,   new string[] { ""Pyrelord"", ""Scorch Sovereign"", ""Inferna"", ""Kindleheart"" } },
        { Element.Water,  new string[] { ""Aqualord"", ""Tide Sovereign"", ""Nerissa"", ""Seabright"" } },
        { Element.Earth,  new string[] { ""Terraguard"", ""Stone Sovereign"", ""Gaiastrider"", ""Rootmother"" } },
        { Element.Air,    new string[] { ""Zephyr King"", ""Storm Sovereign"", ""Skydancer"", ""Aetheris"" } },
        { Element.Neutral,new string[] { ""Elder Wisp"", ""Prime Shade"", ""Old Mote"", ""Ancestral Drift"" } },

        // new elements - add a few special rares for each
        { Element.Ice, new string[] { ""Frostar"", ""Glacier Monarch"", ""Rimelord"" } },
        { Element.Lightning, new string[] { ""Volt Sovereign"", ""Storm Arch"", ""Thunderlord"" } },
        { Element.Poison, new string[] { ""Venom Regent"", ""Blightmother"", ""Toxarch"" } },
        { Element.Psychic, new string[] { ""Mindseer"", ""Thought Sovereign"", ""Noctem"" } },
        { Element.Metal, new string[] { ""Iron Warden"", ""Alloy King"", ""Forge Lord"" } },
        { Element.Wood, new string[] { ""Grove Matron"", ""Sylvan King"", ""Bramblelord"" } },
        { Element.Light, new string[] { ""Solarch"", ""Luminarch"", ""Dawnsoul"" } },
        { Element.Dark, new string[] { ""Umbrage"", ""Night Sovereign"", ""Ebonlord"" } },
        { Element.Sound, new string[] { ""Echo Regent"", ""Chordmaster"", ""Resonant"" } },
        { Element.Gravity, new string[] { ""Gravemight"", ""Weightlord"", ""Mass Sovereign"" } },
        { Element.Time, new string[] { ""Chronarch"", ""Epoch Sovereign"", ""Hourlord"" } },
        { Element.Space, new string[] { ""Galaxor"", ""Void Sovereign"", ""Astromancer"" } },
        { Element.Plasma, new string[] { ""Corona Warden"", ""Plasmar"", ""Ion Sovereign"" } },
        { Element.Crystal, new string[] { ""Gemarch"", ""Facet Sovereign"", ""Prismarch"" } },
        { Element.Arcane, new string[] { ""Mystarch"", ""Runemaster"", ""Aetherlord"" } },
        { Element.Spirit, new string[] { ""Soulwarden"", ""Seance Sovereign"", ""Phantasm"" } },
        { Element.Steam, new string[] { ""Geyserlord"", ""Boil Regent"", ""Vaporarch"" } },
        { Element.Sand, new string[] { ""Dunemaster"", ""Quicksandlord"", ""Oasarch"" } },
        { Element.Magnetic, new string[] { ""Polarch"", ""Dipole Warden"", ""Flux Sovereign"" } },
        { Element.Ethereal, new string[] { ""Veil Sovereign"", ""Aether Regent"", ""Nethermuse"" } }
    };

    // Legendary unique names per element (very small pools)
    static readonly Dictionary<Element, string[]> legendaryNames = new Dictionary<Element, string[]>
    {
        { Element.Fire, new string[] { ""Pyrothrax"", ""Solarion"" } },
        { Element.Water, new string[] { ""Oceanus"", ""Hydrath"" } },
        { Element.Earth, new string[] { ""Terragon"", ""Gaios"" } },
        { Element.Air, new string[] { ""Aetherion"", ""Zephyrus"" } },
        { Element.Neutral, new string[] { ""Umbraxis"", ""Echofane"" } },

        // include a legendary for each new element where thematic
        { Element.Ice, new string[] { ""Glaciarch"", ""Frostreign"" } },
        { Element.Lightning, new string[] { ""Voltanos"", ""Stormbringer"" } },
        { Element.Poison, new string[] { ""Noxus"", ""Pestilora"" } },
        { Element.Psychic, new string[] { ""Noetarius"", ""Mindcore"" } },
        { Element.Metal, new string[] { ""Forgemaster"", ""Ironsoul"" } },
        { Element.Wood, new string[] { ""Gaiapex"", ""Sylvanus"" } },
        { Element.Light, new string[] { ""Solstice Prime"", ""Luminara"" } },
        { Element.Dark, new string[] { ""Nightrazor"", ""Umbrafang"" } },
        { Element.Sound, new string[] { ""Cantorus"", ""Resonax"" } },
        { Element.Gravity, new string[] { ""Gravion"", ""Abyssal Mass"" } },
        { Element.Time, new string[] { ""Chronos"", ""Aeonlord"" } },
        { Element.Space, new string[] { ""Cosmion"", ""Void Sovereign"" } },
        { Element.Plasma, new string[] { ""Corona Prime"", ""Ionarch"" } },
        { Element.Crystal, new string[] { ""Prismion"", ""Facet Monarch"" } },
        { Element.Arcane, new string[] { ""Aetherius"", ""Arcanum"" } },
        { Element.Spirit, new string[] { ""Eidolon Prime"", ""Soul King"" } },
        { Element.Steam, new string[] { ""Vaporion"", ""Boil Sovereign"" } },
        { Element.Sand, new string[] { ""Dune Emperor"", ""Oasis Warden"" } },
        { Element.Magnetic, new string[] { ""Magnetron"", ""Polaris Prime"" } },
        { Element.Ethereal, new string[] { ""Netheris"", ""Gossam Prime"" } }
    };

    // Evolved-form names per element (stage 1)
    static readonly Dictionary<Element, string[]> evolvedNamesStage1 = new Dictionary<Element, string[]>
    {
        { Element.Fire,   new string[] { ""Pyroclast"", ""Flarewarden"", ""Cinderian"", ""Blaze Sovereign"" } },
        { Element.Water,  new string[] { ""Hydromancer"", ""Tidewarden"", ""Aquarion"", ""Seastone"" } },
        { Element.Earth,  new string[] { ""Gaiaguard"", ""Terrashaper"", ""Stone Sovereign"", ""Rootwarden"" } },
        { Element.Air,    new string[] { ""Skywarden"", ""Gale Sovereign"", ""Aeroarch"", ""Zepherial"" } },
        { Element.Neutral,new string[] { ""Umbramaster"", ""Wispwarden"", ""Echogrove"", ""Motesage"" } },

        // a few evolved name options for the new elements
        { Element.Ice, new string[] { ""Glaciarch"", ""Frostreign"", ""Rime Sovereign"" } },
        { Element.Lightning, new string[] { ""Stormheart"", ""Voltarch"", ""Thunder Sovereign"" } },
        { Element.Poison, new string[] { ""Blightlord"", ""Venomatrix"", ""Toxmancer"" } },
        { Element.Psychic, new string[] { ""Mindwarden"", ""Psychemaster"", ""Noetarch"" } },
        { Element.Metal, new string[] { ""Forgebearer"", ""Ironwarden"", ""Alloyarch"" } },
        { Element.Wood, new string[] { ""Sylvamother"", ""Grovewarden"", ""Bramblearch"" } },
        { Element.Light, new string[] { ""Radiancer"", ""Solguard"", ""Lucentarch"" } },
        { Element.Dark, new string[] { ""Night Sovereign"", ""Umbralord"", ""Shadowarch"" } },
        { Element.Sound, new string[] { ""Resonarch"", ""Chorus King"", ""Echowarden"" } },
        { Element.Gravity, new string[] { ""Massarch"", ""Gravemaster"", ""Tidepull"" } },
        { Element.Time, new string[] { ""Chronarch"", ""Epochwarden"", ""Temposage"" } },
        { Element.Space, new string[] { ""Cosmarch"", ""Voidwarden"", ""Starborne"" } },
        { Element.Plasma, new string[] { ""Coronaarch"", ""Ionsovereign"", ""Fluxlord"" } },
        { Element.Crystal, new string[] { ""Prismarch"", ""Gemlord"", ""Facetkeeper"" } },
        { Element.Arcane, new string[] { ""Aetherarch"", ""Runemaster"", ""Spellwarden"" } },
        { Element.Spirit, new string[] { ""Soulwarden"", ""Phantasmarch"", ""Eidolonarch"" } },
        { Element.Steam, new string[] { ""Vaporwarden"", ""Geyserlord"", ""Scaldarch"" } },
        { Element.Sand, new string[] { ""Dunemaster"", ""Quicksandlord"", ""Oasarch"" } },
        { Element.Magnetic, new string[] { ""Fluxwarden"", ""Polarch"", ""Dipole King"" } },
        { Element.Ethereal, new string[] { ""Veilbound"", ""Aetherlord"", ""Gossamer King"" } }
    };

    // Rarity-based prefixes
    static readonly Dictionary<Rarity, string> rarityPrefix = new Dictionary<Rarity, string>
    {
        { Rarity.Common, "" },
        { Rarity.Uncommon, ""Greater "" },
        { Rarity.Rare, ""Rare "" },
        { Rarity.Epic, ""Ancient "" },
        { Rarity.Legendary, "" }
    };

    // Main public method
    public static string GetName(Element element, Rarity rarity)
    {
        // Legendary: try legendary names first
        if (rarity == Rarity.Legendary)
        {
            if (legendaryNames.TryGetValue(element, out var ln) && ln.Length > 0)
                return ln[Random.Range(0, ln.Length)];
        }

        // Epic and Rare: prefer rareNames pool sometimes
        if (rarity == Rarity.Epic || rarity == Rarity.Rare)
        {
            if (rareNames.TryGetValue(element, out var rn) && rn.Length > 0)
            {
                float pickChance = (rarity == Rarity.Epic) ? 0.85f : 0.6f;
                if (Random.value < pickChance)
                    return rn[Random.Range(0, rn.Length)];
            }
        }

        // Fallback: pick from base pool and optionally prefix by rarity
        string baseName = ""Creature"";
        if (baseNames.TryGetValue(element, out var pool) && pool.Length > 0)
            baseName = pool[Random.Range(0, pool.Length)];

        string prefix = rarityPrefix.ContainsKey(rarity) ? rarityPrefix[rarity] : """";
        string result = string.IsNullOrEmpty(prefix) ? baseName : prefix + baseName;

        // Small chance to append suffix
        if (Random.value < 0.05f)
        {
            string[] suffixes = new string[] { "" the Swift"", "" the Stalwart"", "" the Warden"", "" of the Vale"", "" of the Hollow"" };
            result += suffixes[Random.Range(0, suffixes.Length)];
        }

        return result;
    }

    // Evolved name getter (for evolved forms)
    public static string GetEvolvedName(Element element, Rarity rarity, int stage = 1)
    {
        if (rarity == Rarity.Legendary)
        {
            if (legendaryNames.TryGetValue(element, out var ln) && ln.Length > 0)
                return ln[Random.Range(0, ln.Length)];
        }

        if (stage == 1)
        {
            if (evolvedNamesStage1.TryGetValue(element, out var arr) && arr.Length > 0)
            {
                string prefix = rarityPrefix.ContainsKey(rarity) ? rarityPrefix[rarity] : """";
                string chosen = arr[Random.Range(0, arr.Length)];
                if (!string.IsNullOrEmpty(prefix)) return prefix + chosen;
                return chosen;
            }
        }

        return GetName(element, rarity);
    }
}
",

            // EvolutionManager.cs
            ["Scripts/EvolutionManager.cs"] = @"using UnityEngine;

public static class EvolutionManager
{
    public static bool ApplyEvolution(CreatureData c)
    {
        if (c == null) return false;
        if (c.isEvolved) return false;
        if (c.rarity == Rarity.Legendary) return false;
        if (c.nextEvolutionLevel <= 0) return false;
        if (c.level < c.nextEvolutionLevel) return false;

        float hpMult = 1.25f + ((int)c.rarity) * 0.07f;
        float atkMult = 1.15f + ((int)c.rarity) * 0.04f;
        float defMult = 1.12f + ((int)c.rarity) * 0.03f;
        float xpMult = 1.25f + ((int)c.rarity) * 0.25f;

        c.maxHP = Mathf.Max(1, Mathf.RoundToInt(c.maxHP * hpMult));
        c.attack = Mathf.Max(1, Mathf.RoundToInt(c.attack * atkMult));
        c.defense = Mathf.Max(0, Mathf.RoundToInt(c.defense * defMult));
        c.xpReward = Mathf.Max(1, Mathf.RoundToInt(c.xpReward * xpMult));
        c.currentHP = c.maxHP;

        c.isEvolved = true;
        c.evolutionStage = Mathf.Max(1, c.evolutionStage + 1);
        c.nextEvolutionLevel = -1;

        string newName = CreatureNamer.GetEvolvedName(c.element, c.rarity, c.evolutionStage);
        c.creatureName = $""{newName} Lvl{c.level}"";

        Debug.Log($""Creature evolved into {c.creatureName} (rarity: {c.rarity})"");
        return true;
    }
}
",

            // CreatureSpawner.cs
            ["Scripts/CreatureSpawner.cs"] = @"using UnityEngine;
using System.Collections.Generic;

[System.Serializable]
public struct RarityWeight
{
    public Rarity rarity;
    public int weight;
}

public class CreatureSpawner : MonoBehaviour
{
    [Header(""Spawner Settings"")]
    public GameObject creaturePrefab;
    public int spawnCount = 4;
    public float spawnRadius = 6f;
    public float spawnYOffset = 0.5f;
    public float spawnInterval = 8f;
    public bool startEnabled = true;

    [Header(""Element & Levels"")]
    public Element[] possibleElements;
    public int minLevel = 1;
    public int maxLevel = 3;

    [Header(""Rarity Settings"")]
    public RarityWeight[] rarityWeights = new RarityWeight[] {
        new RarityWeight { rarity = Rarity.Common, weight = 60 },
        new RarityWeight { rarity = Rarity.Uncommon, weight = 25 },
        new RarityWeight { rarity = Rarity.Rare, weight = 10 },
        new RarityWeight { rarity = Rarity.Epic, weight = 4 },
        new RarityWeight { rarity = Rarity.Legendary, weight = 1 }
    };

    bool spawningEnabled = true;

    void Start()
    {
        spawningEnabled = startEnabled;
        if (spawningEnabled)
            StartCoroutine(SpawnRoutine());
    }

    public void EnableSpawning(bool enabled)
    {
        spawningEnabled = enabled;
        StopAllCoroutines();
        if (enabled)
            StartCoroutine(SpawnRoutine());
        else
            DespawnAllChildren();
    }

    System.Collections.IEnumerator SpawnRoutine()
    {
        SpawnBatch();
        while (spawningEnabled)
        {
            yield return new WaitForSeconds(spawnInterval);
            SpawnBatch();
        }
    }

    void SpawnBatch()
    {
        int existing = 0;
        foreach (Transform t in transform)
        {
            if (t.GetComponent<Creature>() != null) existing++;
        }

        int toSpawn = Mathf.Max(0, spawnCount - existing);
        for (int i = 0; i < toSpawn; i++)
        {
            Vector3 pos = transform.position + new Vector3(
                Random.Range(-spawnRadius, spawnRadius),
                spawnYOffset,
                Random.Range(-spawnRadius, spawnRadius)
            );

            GameObject go;
            if (creaturePrefab != null)
                go = Instantiate(creaturePrefab, pos, Quaternion.identity, transform);
            else
            {
                go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                Destroy(go.GetComponent<Collider>());
                go.transform.SetParent(transform);
                go.transform.position = pos;
                go.transform.localScale = Vector3.one * 1.0f;
            }

            var cr = go.GetComponent<Creature>();
            if (cr == null) cr = go.AddComponent<Creature>();

            cr.level = Random.Range(minLevel, maxLevel + 1);
            cr.maxHP = 25 + cr.level * 10;
            cr.currentHP = cr.maxHP;
            cr.attack = 6 + cr.level * 3;
            cr.defense = 2 + cr.level;
            cr.xpReward = 10 + cr.level * 5;
            cr.isWild = true;

            if (possibleElements != null && possibleElements.Length > 0)
                cr.element = possibleElements[Random.Range(0, possibleElements.Length)];
            else
                cr.element = Element.Neutral;

            cr.rarity = ChooseRarityByWeight();

            cr.abilities = new Ability[] {
                new Ability(""Bash"", Element.Neutral, 8),
                new Ability(cr.element.ToString() + "" Strike"", cr.element, 10)
            };

            cr.creatureName = CreatureNamer.GetName(cr.element, cr.rarity) + $"" Lvl{cr.level}"";

            cr.isEvolved = false;
            cr.evolutionStage = 0;
            cr.nextEvolutionLevel = ComputeNextEvolutionLevel(cr.rarity, cr.level);

            var rend = go.GetComponent<Renderer>();
            if (rend != null)
            {
                Color baseColor = Color.gray;
                switch (cr.element)
                {
                    case Element.Fire: baseColor = Color.red; break;
                    case Element.Water: baseColor = Color.blue; break;
                    case Element.Earth: baseColor = new Color(0.5f, 0.25f, 0f); break;
                    case Element.Air: baseColor = Color.white; break;
                    default: baseColor = Color.gray; break;
                }

                Color rarityTint = GetTintForRarity(cr.rarity);
                rend.material.color = Color.Lerp(baseColor, rarityTint, 0.35f);
            }

            float scaleMult = 1f + GetScaleForRarity(cr.rarity);
            go.transform.localScale = Vector3.one * scaleMult;

            var col = go.GetComponent<SphereCollider>();
            if (col == null) col = go.AddComponent<SphereCollider>();
            col.isTrigger = true;
            col.radius = 0.9f;
        }
    }

    int ComputeNextEvolutionLevel(Rarity r, int currentLevel)
    {
        if (r == Rarity.Legendary) return -1;

        switch (r)
        {
            case Rarity.Common: return currentLevel + Random.Range(8, 13);
            case Rarity.Uncommon: return currentLevel + Random.Range(14, 21);
            case Rarity.Rare: return currentLevel + Random.Range(20, 28);
            case Rarity.Epic: return currentLevel + Random.Range(28, 36);
            default: return currentLevel + Random.Range(10, 18);
        }
    }

    Rarity ChooseRarityByWeight()
    {
        int total = 0;
        foreach (var rw in rarityWeights) total += Mathf.Max(0, rw.weight);
        if (total <= 0) return Rarity.Common;
        int roll = Random.Range(0, total);
        int accum = 0;
        foreach (var rw in rarityWeights)
        {
            accum += Mathf.Max(0, rw.weight);
            if (roll < accum) return rw.rarity;
        }
        return rarityWeights.Length > 0 ? rarityWeights[0].rarity : Rarity.Common;
    }

    Color GetTintForRarity(Rarity r)
    {
        switch (r)
        {
            case Rarity.Uncommon: return Color.green;
            case Rarity.Rare: return new Color(0.25f, 0.5f, 1f);
            case Rarity.Epic: return new Color(0.6f, 0.3f, 1f);
            case Rarity.Legendary: return new Color(1f, 0.85f, 0.2f);
            default: return Color.white;
        }
    }

    float GetScaleForRarity(Rarity r)
    {
        switch (r)
        {
            case Rarity.Uncommon: return 0.06f;
            case Rarity.Rare: return 0.12f;
            case Rarity.Epic: return 0.22f;
            case Rarity.Legendary: return 0.35f;
            default: return 0f;
        }
    }

    void DespawnAllChildren()
    {
        var list = new List<Transform>();
        foreach (Transform t in transform) list.Add(t);
        foreach (var t in list) Destroy(t.gameObject);
    }
}
",

            // VisualDatabase.cs
            ["Scripts/VisualDatabase.cs"] = @"using UnityEngine;

[CreateAssetMenu(fileName = ""VisualDatabase"", menuName = ""Visuals/Visual Database"", order = 100)]
public class VisualDatabase : ScriptableObject
{
    [System.Serializable]
    public class ElementVisual
    {
        public Element element;
        public GameObject[] stagePrefabs;
        public Sprite[] thumbnails;
        public float baseScale = 1f;
        public float evolvedScale = 1.2f;
    }

    public ElementVisual[] elementVisuals;
    public Color commonTint = Color.white;
    public Color uncommonTint = Color.green;
    public Color rareTint = new Color(0.25f, 0.5f, 1f);
    public Color epicTint = new Color(0.6f, 0.3f, 1f);
    public Color legendaryTint = new Color(1f, 0.85f, 0.2f);

    public ElementVisual GetElementVisual(Element e)
    {
        for (int i = 0; i < elementVisuals.Length; i++)
            if (elementVisuals[i].element == e) return elementVisuals[i];
        return null;
    }

    public Color GetTintForRarity(Rarity r)
    {
        switch (r)
        {
            case Rarity.Uncommon: return uncommonTint;
            case Rarity.Rare: return rareTint;
            case Rarity.Epic: return epicTint;
            case Rarity.Legendary: return legendaryTint;
            default: return commonTint;
        }
    }
}
",

            // VisualManager.cs
            ["Scripts/VisualManager.cs"] = @"using UnityEngine;
using UnityEngine.UI;

[DisallowMultipleComponent]
public class VisualManager : MonoBehaviour
{
    public static VisualManager Instance;
    public VisualDatabase db;

    void Awake()
    {
        if (Instance == null) Instance = this;
        else { Destroy(gameObject); return; }
        DontDestroyOnLoad(gameObject);
    }

    public GameObject GetPrefab(Element element, int evolutionStage)
    {
        if (db == null) return null;
        var ev = db.GetElementVisual(element);
        if (ev == null || ev.stagePrefabs == null || ev.stagePrefabs.Length == 0) return null;
        int idx = Mathf.Clamp(evolutionStage, 0, ev.stagePrefabs.Length - 1);
        return ev.stagePrefabs[idx];
    }

    public Sprite GetThumbnail(Element element, int evolutionStage)
    {
        if (db == null) return null;
        var ev = db.GetElementVisual(element);
        if (ev == null || ev.thumbnails == null || ev.thumbnails.Length == 0) return null;
        int idx = Mathf.Clamp(evolutionStage, 0, ev.thumbnails.Length - 1);
        return ev.thumbnails[idx];
    }

    public Color GetTintForRarity(Rarity r)
    {
        if (db == null) return Color.white;
        return db.GetTintForRarity(r);
    }

    public GameObject CreateBattleVisual(CreatureData c, Transform parent = null)
    {
        if (c == null) return null;
        GameObject prefab = GetPrefab(c.element, c.evolutionStage);
        GameObject go;
        if (prefab != null) go = Instantiate(prefab, parent);
        else
        {
            go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            Destroy(go.GetComponent<Collider>());
            if (parent != null) go.transform.SetParent(parent, false);
        }

        var ev = db != null ? db.GetElementVisual(c.element) : null;
        float scale = (c.isEvolved && ev != null) ? ev.evolvedScale : (ev != null ? ev.baseScale : 1f);
        go.transform.localScale = Vector3.one * scale;
        ApplyTintToObject(go, GetTintForRarity(c.rarity));
        return go;
    }

    public CreatureVisual EnsureCreatureVisual(Component container)
    {
        if (container == null) return null;
        var cv = container.GetComponentInChildren<CreatureVisual>();
        if (cv != null) return cv;
        cv = container.gameObject.GetComponent<CreatureVisual>();
        if (cv == null) cv = container.gameObject.AddComponent<CreatureVisual>();
        cv.visualManager = this;
        return cv;
    }

    public void ApplyTintToObject(GameObject go, Color tint)
    {
        if (go == null) return;
        var meshRenderers = go.GetComponentsInChildren<MeshRenderer>(true);
        foreach (var mr in meshRenderers)
        {
            if (mr.sharedMaterial != null)
            {
                mr.material = new Material(mr.material);
                mr.material.color = mr.material.color * tint;
            }
        }

        var srenders = go.GetComponentsInChildren<SpriteRenderer>(true);
        foreach (var sr in srenders) sr.color = sr.color * tint;

        var images = go.GetComponentsInChildren<Image>(true);
        foreach (var img in images) img.color = img.color * tint;
    }
}
",

            // CreatureVisual.cs
            ["Scripts/CreatureVisual.cs"] = @"using UnityEngine;

public class CreatureVisual : MonoBehaviour
{
    [HideInInspector] public VisualManager visualManager;
    GameObject visualInstance;
    Element currentElement = Element.Neutral;
    int currentStage = 0;
    Rarity currentRarity = Rarity.Common;
    public Vector3 localOffset = Vector3.zero;

    public void InitializeFromCreature(Creature creature)
    {
        if (creature == null) return;
        if (visualManager == null) visualManager = VisualManager.Instance;

        CreatureData tmp = new CreatureData
        {
            creatureName = creature.creatureName,
            element = creature.element,
            level = creature.level,
            maxHP = creature.maxHP,
            currentHP = creature.currentHP,
            attack = creature.attack,
            defense = creature.defense,
            abilities = creature.abilities,
            xpReward = creature.xpReward,
            rarity = creature.rarity,
            isCaptured = !creature.isWild,
            isProtected = false,
            isEvolved = creature.isEvolved,
            evolutionStage = creature.evolutionStage,
            nextEvolutionLevel = creature.nextEvolutionLevel
        };

        UpdateVisual(tmp);
    }

    public void UpdateVisual(CreatureData data)
    {
        if (data == null) return;
        if (visualManager == null) visualManager = VisualManager.Instance;

        bool needRebuild = (visualInstance == null) || data.element != currentElement || data.evolutionStage != currentStage;
        currentElement = data.element;
        currentStage = data.evolutionStage;
        currentRarity = data.rarity;

        if (needRebuild)
        {
            if (visualInstance != null) Destroy(visualInstance);

            GameObject prefab = visualManager != null ? visualManager.GetPrefab(data.element, data.evolutionStage) : null;
            if (prefab != null)
            {
                visualInstance = Instantiate(prefab, transform);
                visualInstance.transform.localPosition = localOffset;
                var ev = visualManager != null ? visualManager.db.GetElementVisual(data.element) : null;
                float scale = (data.isEvolved && ev != null) ? ev.evolvedScale : (ev != null ? ev.baseScale : 1f);
                visualInstance.transform.localScale = Vector3.one * scale;
            }
            else
            {
                GameObject fallback = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                Destroy(fallback.GetComponent<Collider>());
                visualInstance = fallback;
                visualInstance.transform.SetParent(transform, false);
                visualInstance.transform.localScale = Vector3.one * 0.9f;
                visualInstance.transform.localPosition = localOffset;
            }
        }

        if (visualManager != null && visualInstance != null)
        {
            visualManager.ApplyTintToObject(visualInstance, visualManager.GetTintForRarity(data.rarity));
        }
    }

    public void ClearVisual()
    {
        if (visualInstance != null) { Destroy(visualInstance); visualInstance = null; }
    }
}
",

            // PlayerRosterManager.cs
            ["Scripts/PlayerRosterManager.cs"] = @"using System.Collections.Generic;
using UnityEngine;
using System;

[DisallowMultipleComponent]
public class PlayerRosterManager : MonoBehaviour
{
    public static PlayerRosterManager Instance;

    [Header(""Roster Settings"")]
    public int teamMaxSize = 4;

    private List<CreatureData> team = new List<CreatureData>();
    private List<CreatureData> box = new List<CreatureData>();
    public event Action OnRosterChanged;

    void Awake()
    {
        if (Instance == null) Instance = this;
        else { Destroy(gameObject); return; }
        DontDestroyOnLoad(gameObject);
    }

    void Start()
    {
        if (team.Count == 0) EnsureStarterCreature();
    }

    void EnsureStarterCreature()
    {
        if (team.Count > 0) return;

        CreatureData starter = new CreatureData
        {
            creatureName = CreatureNamer.GetName(Element.Fire, Rarity.Common),
            element = Element.Fire,
            level = 1,
            maxHP = 60,
            currentHP = 60,
            attack = 12,
            defense = 4,
            xpReward = 0,
            abilities = new Ability[] {
                new Ability(""Ember"", Element.Fire, 14),
                new Ability(""Quick Strike"", Element.Neutral, 8),
                new Ability(""Flame Kick"", Element.Fire, 10),
                new Ability(""Guard"", Element.Neutral, 0)
            },
            rarity = Rarity.Common,
            isCaptured = true,
            isEvolved = false,
            evolutionStage = 0,
            nextEvolutionLevel = -1
        };

        AddCreatureToTeamOrBox(starter);
    }

    public bool AddCreatureToTeamOrBox(CreatureData creature)
    {
        if (creature == null) return false;
        CreatureData clone = CloneCreatureData(creature);
        clone.isCaptured = true;

        if (team.Count < teamMaxSize)
        {
            team.Add(clone);
            OnRosterChanged?.Invoke();
            return true;
        }
        else
        {
            box.Add(clone);
            OnRosterChanged?.Invoke();
            return false;
        }
    }

    public void AddToBox(CreatureData creature)
    {
        if (creature == null) return;
        box.Add(CloneCreatureData(creature));
        OnRosterChanged?.Invoke();
    }

    public bool SendTeamToBox(int teamIndex)
    {
        if (teamIndex < 0 || teamIndex >= team.Count) return false;
        var c = team[teamIndex];
        box.Add(c);
        team.RemoveAt(teamIndex);
        OnRosterChanged?.Invoke();
        return true;
    }

    public bool WithdrawBoxToTeam(int boxIndex)
    {
        if (boxIndex < 0 || boxIndex >= box.Count) return false;
        if (team.Count >= teamMaxSize) return false;
        var c = box[boxIndex];
        team.Add(c);
        box.RemoveAt(boxIndex);
        OnRosterChanged?.Invoke();
        return true;
    }

    public bool DeleteFromTeam(int teamIndex)
    {
        if (teamIndex < 0 || teamIndex >= team.Count) return false;
        team.RemoveAt(teamIndex);
        OnRosterChanged?.Invoke();
        return true;
    }
    public bool DeleteFromBox(int boxIndex)
    {
        if (boxIndex < 0 || boxIndex >= box.Count) return false;
        box.RemoveAt(boxIndex);
        OnRosterChanged?.Invoke();
        return true;
    }

    public bool SwapTeamOrder(int indexA, int indexB)
    {
        if (indexA < 0 || indexA >= team.Count) return false;
        if (indexB < 0 || indexB >= team.Count) return false;
        if (indexA == indexB) return false;
        var tmp = team[indexA];
        team[indexA] = team[indexB];
        team[indexB] = tmp;
        OnRosterChanged?.Invoke();
        return true;
    }

    public bool SetActiveByIndex(int index)
    {
        if (index < 0 || index >= team.Count) return false;
        if (index == 0) return true;
        var c = team[index];
        team.RemoveAt(index);
        team.Insert(0, c);
        OnRosterChanged?.Invoke();
        return true;
    }

    public bool PromoteToActive(int index)
    {
        return SetActiveByIndex(index);
    }

    public void SortTeamByLevel()
    {
        if (team == null || team.Count <= 1) return;
        team.Sort((a, b) => b.level.CompareTo(a.level));
        OnRosterChanged?.Invoke();
    }

    public CreatureData GetActiveCreature()
    {
        if (team.Count == 0) return null;
        return team[0];
    }

    public void SetActiveCreature(CreatureData data)
    {
        if (data == null) return;
        if (team.Count == 0) team.Add(CloneCreatureData(data));
        else team[0] = CloneCreatureData(data);
        OnRosterChanged?.Invoke();
    }

    public CreatureData[] GetTeamArray() => team.ToArray();
    public CreatureData[] GetBoxArray() => box.ToArray();

    public void SetTeamAndBox(CreatureData[] teamArr, CreatureData[] boxArr)
    {
        team.Clear();
        box.Clear();
        if (teamArr != null) foreach (var c in teamArr) team.Add(CloneCreatureData(c));
        if (boxArr != null) foreach (var c in boxArr) box.Add(CloneCreatureData(c));
        OnRosterChanged?.Invoke();
    }

    CreatureData CloneCreatureData(CreatureData src)
    {
        if (src == null) return null;
        CreatureData clone = new CreatureData();
        clone.creatureName = src.creatureName;
        clone.element = src.element;
        clone.level = src.level;
        clone.maxHP = src.maxHP;
        clone.currentHP = src.currentHP;
        clone.attack = src.attack;
        clone.defense = src.defense;
        clone.abilities = src.abilities != null ? (Ability[])src.abilities.Clone() : null;
        clone.xpReward = src.xpReward;
        clone.rarity = src.rarity;
        clone.isCaptured = src.isCaptured;
        clone.isProtected = src.isProtected;
        clone.isEvolved = src.isEvolved;
        clone.evolutionStage = src.evolutionStage;
        clone.nextEvolutionLevel = src.nextEvolutionLevel;
        return clone;
    }

    public int TeamCount => team.Count;
    public int BoxCount => box.Count;
    public CreatureData GetTeamAt(int idx) => (idx >= 0 && idx < team.Count) ? team[idx] : null;
    public CreatureData GetBoxAt(int idx) => (idx >= 0 && idx < box.Count) ? box[idx] : null;
}
",

            // RosterUI.cs
            ["Scripts/RosterUI.cs"] = @"using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class RosterUI : MonoBehaviour
{
    [Header(""Panels"")]
    public GameObject rosterPanel;
    public Transform teamSlotsParent;
    public GameObject teamSlotPrefab;
    public Transform boxContentParent;
    public GameObject boxItemPrefab;

    [Header(""Swap & Sort Controls"")]
    public Button swapModeButton;
    public Text swapModeIndicatorText;
    public Button autoSortButton;

    [Header(""Settings"")]
    public int maxTeamDisplay = 4;
    public Color selectionColor = new Color(1f, 0.9f, 0.4f);
    public Color normalColor = Color.white;

    private List<GameObject> teamSlotObjects = new List<GameObject>();
    private List<GameObject> boxItemObjects = new List<GameObject>();

    private bool swapModeActive = false;
    private int firstSwapIndex = -1;

    void Start()
    {
        if (PlayerRosterManager.Instance != null)
            PlayerRosterManager.Instance.OnRosterChanged += RefreshUI;

        if (swapModeButton != null) swapModeButton.onClick.AddListener(ToggleSwapMode);
        if (autoSortButton != null) autoSortButton.onClick.AddListener(OnAutoSortPressed);

        if (teamSlotsParent != null)
        {
            if (teamSlotsParent.childCount > 0)
            {
                teamSlotObjects.Clear();
                foreach (Transform t in teamSlotsParent) teamSlotObjects.Add(t.gameObject);
            }
            else if (teamSlotPrefab != null)
            {
                for (int i = 0; i < maxTeamDisplay; i++)
                {
                    var go = Instantiate(teamSlotPrefab, teamSlotsParent);
                    teamSlotObjects.Add(go);
                }
            }
        }

        if (rosterPanel != null) rosterPanel.SetActive(false);
        RefreshUI();
    }

    public void OpenRosterPanel()
    {
        if (rosterPanel != null) rosterPanel.SetActive(true);
        RefreshUI();
    }

    public void CloseRosterPanel()
    {
        if (rosterPanel != null) rosterPanel.SetActive(false);
    }

    public void RefreshUI()
    {
        for (int i = 0; i < teamSlotObjects.Count; i++)
        {
            var slotObj = teamSlotObjects[i];
            var nameText = slotObj.transform.Find(""NameText"")?.GetComponent<Text>();
            var hpText = slotObj.transform.Find(""HPText"")?.GetComponent<Text>();
            var promoteButton = slotObj.transform.Find(""SetActiveButton"")?.GetComponent<Button>();
            var sendBoxButton = slotObj.transform.Find(""SendBoxButton"")?.GetComponent<Button>();
            var deleteButton = slotObj.transform.Find(""DeleteButton"")?.GetComponent<Button>();
            var slotButton = slotObj.GetComponent<Button>();
            var slotImage = slotObj.GetComponent<Image>();

            if (promoteButton != null) { promoteButton.onClick.RemoveAllListeners(); }
            if (sendBoxButton != null) { sendBoxButton.onClick.RemoveAllListeners(); }
            if (deleteButton != null) { deleteButton.onClick.RemoveAllListeners(); }
            if (slotButton != null) { slotButton.onClick.RemoveAllListeners(); }

            if (i < PlayerRosterManager.Instance.TeamCount)
            {
                var c = PlayerRosterManager.Instance.GetTeamAt(i);
                if (nameText != null) nameText.text = $""{c.creatureName} [{c.rarity}]"";
                if (hpText != null) hpText.text = $""HP {c.currentHP}/{c.maxHP}"";

                if (promoteButton != null)
                {
                    promoteButton.gameObject.SetActive(true);
                    int idx = i;
                    promoteButton.onClick.AddListener(() => OnPromote(idx));
                }

                if (sendBoxButton != null)
                {
                    sendBoxButton.gameObject.SetActive(true);
                    int idx = i;
                    sendBoxButton.onClick.AddListener(() => OnSendToBox(idx));
                }

                if (deleteButton != null)
                {
                    deleteButton.gameObject.SetActive(true);
                    int idx = i;
                    deleteButton.onClick.AddListener(() => OnDeleteFromTeam(idx));
                }

                if (slotButton != null)
                {
                    int idx = i;
                    slotButton.onClick.AddListener(() => OnTeamSlotClicked(idx));
                }

                if (slotImage != null)
                {
                    if (swapModeActive && firstSwapIndex == i)
                        slotImage.color = selectionColor;
                    else
                        slotImage.color = normalColor;
                }

                var thumbnail = slotObj.transform.Find(""ThumbnailImage"")?.GetComponent<Image>();
                if (thumbnail != null && VisualManager.Instance != null)
                {
                    Sprite thumb = VisualManager.Instance.GetThumbnail(c.element, c.evolutionStage);
                    thumbnail.sprite = thumb;
                    thumbnail.color = VisualManager.Instance.GetTintForRarity(c.rarity);
                }
            }
            else
            {
                if (nameText != null) nameText.text = ""Empty"";
                if (hpText != null) hpText.text = """";
                if (promoteButton != null) promoteButton.gameObject.SetActive(false);
                if (sendBoxButton != null) sendBoxButton.gameObject.SetActive(false);
                if (deleteButton != null) deleteButton.gameObject.SetActive(false);
                if (slotButton != null) slotButton.onClick.RemoveAllListeners();
                if (slotImage != null) slotImage.color = normalColor;
            }
        }

        foreach (var go in boxItemObjects) Destroy(go);
        boxItemObjects.Clear();

        if (boxItemPrefab != null && boxContentParent != null)
        {
            for (int i = 0; i < PlayerRosterManager.Instance.BoxCount; i++)
            {
                var c = PlayerRosterManager.Instance.GetBoxAt(i);
                var itemGO = Instantiate(boxItemPrefab, boxContentParent);
                boxItemObjects.Add(itemGO);

                var nameText = itemGO.transform.Find(""NameText"")?.GetComponent<Text>();
                var withdrawButton = itemGO.transform.Find(""WithdrawButton"")?.GetComponent<Button>();
                var deleteButton = itemGO.transform.Find(""DeleteButton"")?.GetComponent<Button>();

                if (nameText != null) nameText.text = $""{c.creatureName} [{c.rarity}] Lv{c.level}"";
                if (withdrawButton != null)
                {
                    int idx = i;
                    withdrawButton.onClick.RemoveAllListeners();
                    withdrawButton.onClick.AddListener(() => OnWithdrawFromBox(idx));
                }

                if (deleteButton != null)
                {
                    int idx = i;
                    deleteButton.onClick.RemoveAllListeners();
                    deleteButton.onClick.AddListener(() => OnDeleteFromBox(idx));
                }

                var thumbnail = itemGO.transform.Find(""ThumbnailImage"")?.GetComponent<Image>();
                if (thumbnail != null && VisualManager.Instance != null)
                {
                    Sprite thumb = VisualManager.Instance.GetThumbnail(c.element, c.evolutionStage);
                    thumbnail.sprite = thumb;
                    thumbnail.color = VisualManager.Instance.GetTintForRarity(c.rarity);
                }
            }
        }

        if (swapModeIndicatorText != null)
        {
            swapModeIndicatorText.text = swapModeActive ? (firstSwapIndex >= 0 ? $""Swap mode: select another slot (first: {firstSwapIndex + 1})"" : ""Swap mode: select first slot"") : ""Swap mode: off"";
        }
    }

    void OnPromote(int teamIndex)
    {
        if (PlayerRosterManager.Instance.PromoteToActive(teamIndex)) RefreshUI();
    }

    void OnSendToBox(int teamIndex)
    {
        if (PlayerRosterManager.Instance.SendTeamToBox(teamIndex)) RefreshUI();
    }

    void OnWithdrawFromBox(int boxIndex)
    {
        bool success = PlayerRosterManager.Instance.WithdrawBoxToTeam(boxIndex);
        if (!success) Debug.Log(""Team is full. Send someone to box first."");
        RefreshUI();
    }

    void OnDeleteFromTeam(int teamIndex)
    {
        PlayerRosterManager.Instance.DeleteFromTeam(teamIndex);
        RefreshUI();
    }

    void OnDeleteFromBox(int boxIndex)
    {
        PlayerRosterManager.Instance.DeleteFromBox(boxIndex);
        RefreshUI();
    }

    void ToggleSwapMode()
    {
        swapModeActive = !swapModeActive;
        firstSwapIndex = -1;
        RefreshUI();
    }

    void OnTeamSlotClicked(int index)
    {
        if (!swapModeActive) return;
        if (firstSwapIndex < 0) { firstSwapIndex = index; RefreshUI(); return; }
        int second = index;
        if (firstSwapIndex == second) { firstSwapIndex = -1; RefreshUI(); return; }
        bool swapped = PlayerRosterManager.Instance.SwapTeamOrder(firstSwapIndex, second);
        firstSwapIndex = -1;
        RefreshUI();
    }

    void OnAutoSortPressed()
    {
        PlayerRosterManager.Instance.SortTeamByLevel();
        RefreshUI();
    }

    private void OnDestroy()
    {
        if (PlayerRosterManager.Instance != null) PlayerRosterManager.Instance.OnRosterChanged -= RefreshUI;
    }
}
",

            // QuestEnums.cs
            ["Scripts/QuestEnums.cs"] = @"public enum QuestStatus
{
    NotStarted = 0,
    Active = 1,
    Completed = 2,
    Rewarded = 3
}

public enum QuestObjectiveType
{
    CaptureCount,
    CaptureSpecific,
    DeliverCreature
}
",

            // Quest.cs
            ["Scripts/Quest.cs"] = @"using System;

[Serializable]
public class Quest
{
    public int id;
    public string title;
    public string description;
    public QuestObjectiveType objectiveType;
    public Rarity minRarity;
    public int targetCount;
    public int progress;
    public QuestStatus status;
    public CaptureDeviceType rewardDevice = CaptureDeviceType.BasicBall;
    public int rewardAmount = 0;

    public Quest(int id, string title, string desc, QuestObjectiveType type, Rarity minRarity = Rarity.Common, int targetCount = 1)
    {
        this.id = id;
        this.title = title;
        this.description = desc;
        this.objectiveType = type;
        this.minRarity = minRarity;
        this.targetCount = targetCount;
        this.progress = 0;
        this.status = QuestStatus.NotStarted;
    }

    public bool IsComplete()
    {
        if (objectiveType == QuestObjectiveType.CaptureCount || objectiveType == QuestObjectiveType.CaptureSpecific)
            return progress >= targetCount;
        if (objectiveType == QuestObjectiveType.DeliverCreature)
            return progress >= 1;
        return false;
    }
}
",

            // QuestManager.cs
            ["Scripts/QuestManager.cs"] = @"using System.Collections.Generic;
using UnityEngine;

[DisallowMultipleComponent]
public class QuestManager : MonoBehaviour
{
    public static QuestManager Instance;
    private List<Quest> quests = new List<Quest>();
    private int currentQuestIndex = -1;

    void Awake()
    {
        if (Instance == null) Instance = this;
        else { Destroy(gameObject); return; }
        DontDestroyOnLoad(gameObject);
    }

    void Start()
    {
        BuildQuestline();
        if (PlayerRosterManager.Instance != null) PlayerRosterManager.Instance.OnRosterChanged += OnRosterChanged;
        RefreshCurrentQuestIndex();
    }

    void OnDestroy()
    {
        if (PlayerRosterManager.Instance != null) PlayerRosterManager.Instance.OnRosterChanged -= OnRosterChanged;
    }

    void BuildQuestline()
    {
        quests.Clear();

        Quest q1 = new Quest(0, ""Find the Rares"", ""Capture 3 creatures of rarity Rare or higher."", QuestObjectiveType.CaptureCount, Rarity.Rare, 3);
        q1.rewardDevice = CaptureDeviceType.GreatBall; q1.rewardAmount = 3;
        quests.Add(q1);

        Quest q2 = new Quest(1, ""A Greater Catch"", ""Capture an Epic creature (or higher)."", QuestObjectiveType.CaptureSpecific, Rarity.Epic, 1);
        q2.rewardDevice = CaptureDeviceType.UltraBall; q2.rewardAmount = 1;
        quests.Add(q2);

        Quest q3 = new Quest(2, ""Sanctuary"", ""Bring an Epic or Legendary creature to the town sanctuary to protect it."", QuestObjectiveType.DeliverCreature, Rarity.Epic, 1);
        q3.rewardDevice = CaptureDeviceType.MasterBall; q3.rewardAmount = 1;
        quests.Add(q3);

        foreach (var q in quests) if (q.status == QuestStatus.NotStarted) q.status = QuestStatus.NotStarted;
    }

    void RefreshCurrentQuestIndex()
    {
        currentQuestIndex = -1;
        for (int i = 0; i < quests.Count; i++)
        {
            if (quests[i].status == QuestStatus.Active || quests[i].status == QuestStatus.NotStarted)
            {
                currentQuestIndex = i;
                if (quests[i].status == QuestStatus.NotStarted) quests[i].status = QuestStatus.Active;
                break;
            }
        }
    }

    void OnRosterChanged() { UpdateCaptureQuests(); }

    void UpdateCaptureQuests()
    {
        if (currentQuestIndex < 0 || currentQuestIndex >= quests.Count) return;
        var q = quests[currentQuestIndex];
        if (q.status != QuestStatus.Active) return;

        if (q.objectiveType == QuestObjectiveType.CaptureCount || q.objectiveType == QuestObjectiveType.CaptureSpecific)
        {
            int count = 0;
            if (PlayerRosterManager.Instance != null)
            {
                for (int i = 0; i < PlayerRosterManager.Instance.TeamCount; i++)
                {
                    var c = PlayerRosterManager.Instance.GetTeamAt(i);
                    if (c != null && c.isCaptured && c.rarity >= q.minRarity) count++;
                }
                for (int i = 0; i < PlayerRosterManager.Instance.BoxCount; i++)
                {
                    var c = PlayerRosterManager.Instance.GetBoxAt(i);
                    if (c != null && c.isCaptured && c.rarity >= q.minRarity) count++;
                }
            }

            q.progress = Mathf.Min(q.targetCount, count);

            if (q.IsComplete()) CompleteQuest(currentQuestIndex);
        }
    }

    void CompleteQuest(int questIdx)
    {
        var q = quests[questIdx];
        q.status = QuestStatus.Completed;
        GrantQuestReward(q);
        q.status = QuestStatus.Rewarded;

        currentQuestIndex = -1;
        for (int i = questIdx + 1; i < quests.Count; i++)
        {
            if (quests[i].status == QuestStatus.NotStarted) { currentQuestIndex = i; quests[i].status = QuestStatus.Active; break; }
        }

        if (currentQuestIndex == -1) Debug.Log(""All quests in the line completed."");
        SaveManager.Instance?.SaveGame();
    }

    void GrantQuestReward(Quest q)
    {
        if (q.rewardAmount > 0) InventoryManager.Instance?.AddDevice(q.rewardDevice, q.rewardAmount);
    }

    public bool TryDeliverFromTown(Area area)
    {
        if (currentQuestIndex < 0 || currentQuestIndex >= quests.Count) return false;
        var q = quests[currentQuestIndex];
        if (q.objectiveType != QuestObjectiveType.DeliverCreature || q.status != QuestStatus.Active) return false;

        CreatureData found = null;
        int teamIndex = -1;
        int boxIndex = -1;

        if (PlayerRosterManager.Instance != null)
        {
            for (int i = 0; i < PlayerRosterManager.Instance.TeamCount; i++)
            {
                var c = PlayerRosterManager.Instance.GetTeamAt(i);
                if (c != null && c.isCaptured && !c.isProtected && c.rarity >= q.minRarity) { found = c; teamIndex = i; break; }
            }
            if (found == null)
            {
                for (int i = 0; i < PlayerRosterManager.Instance.BoxCount; i++)
                {
                    var c = PlayerRosterManager.Instance.GetBoxAt(i);
                    if (c != null && c.isCaptured && !c.isProtected && c.rarity >= q.minRarity) { found = c; boxIndex = i; break; }
                }
            }
        }

        if (found == null) { Debug.Log(""No suitable creature available to deliver for the quest.""); return false; }

        found.isProtected = true;
        q.progress = 1;
        q.status = QuestStatus.Completed;
        Debug.Log($""Delivered {found.creatureName} to sanctuary at {area?.areaName}. Quest complete."");
        GrantQuestReward(q);
        q.status = QuestStatus.Rewarded;

        currentQuestIndex = -1;
        for (int i = 0; i < quests.Count; i++) if (quests[i].status == QuestStatus.NotStarted) { currentQuestIndex = i; quests[i].status = QuestStatus.Active; break; }

        SaveManager.Instance?.SaveGame();
        return true;
    }

    public string GetCurrentQuestTitle()
    {
        if (currentQuestIndex < 0 || currentQuestIndex >= quests.Count) return ""No Active Quest"";
        return quests[currentQuestIndex].title;
    }

    public string GetCurrentQuestDescription()
    {
        if (currentQuestIndex < 0 || currentQuestIndex >= quests.Count) return """";
        var q = quests[currentQuestIndex];
        string prog = """";
        if (q.objectiveType == QuestObjectiveType.CaptureCount || q.objectiveType == QuestObjectiveType.CaptureSpecific) prog = $""Progress: {q.progress}/{q.targetCount}"";
        else if (q.objectiveType == QuestObjectiveType.DeliverCreature) prog = q.progress >= 1 ? ""Delivered"" : ""Deliver an eligible creature at the town sanctuary."";
        return $""{q.description}\n{prog}"";
    }

    [System.Serializable]
    public struct QuestSaveState { public int id; public QuestStatus status; public int progress; }

    public QuestSaveState[] GetQuestSaveStates()
    {
        var arr = new List<QuestSaveState>();
        foreach (var q in quests) arr.Add(new QuestSaveState { id = q.id, status = q.status, progress = q.progress });
        return arr.ToArray();
    }

    public void SetQuestSaveStates(QuestSaveState[] arr)
    {
        if (arr == null) return;
        if (quests == null || quests.Count == 0) BuildQuestline();
        foreach (var s in arr)
        {
            var q = quests.Find(x => x.id == s.id);
            if (q != null) { q.status = s.status; q.progress = s.progress; }
        }
        RefreshCurrentQuestIndex();
    }
}
",

            // BattleSystem.cs
            ["Scripts/BattleSystem.cs"] = @"using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class BattleSystem : MonoBehaviour
{
    public static BattleSystem Instance;

    [Header(""UI Elements"")]
    public GameObject battlePanel;
    public Text playerNameText;
    public Text playerHPText;
    public Text enemyNameText;
    public Text enemyHPText;
    public Button[] abilityButtons;
    public Text messageLogText;
    public Button runButton;

    [Header(""Capture UI"")]
    public Button captureOpenButton;
    public GameObject capturePanel;
    public Button[] captureDeviceButtons;
    public Text[] captureDeviceCountTexts;

    [Header(""Battle Visuals"")]
    public Transform battlePlayerPos;
    public Transform battleEnemyPos;
    public GameObject creatureBattlePrefab;

    private CreatureData playerCreature;
    private CreatureData enemyCreature;
    private GameObject playerCreatureGO;
    private GameObject enemyCreatureGO;
    private GameObject playerGameObjectRef;

    private bool playerTurn = true;
    private bool battleActive = false;

    void Awake()
    {
        if (Instance == null) Instance = this;
        else { Destroy(gameObject); return; }
    }

    void Start()
    {
        if (battlePanel != null) battlePanel.SetActive(false);
        if (capturePanel != null) capturePanel.SetActive(false);

        for (int i = 0; i < abilityButtons.Length; i++) { int idx = i; abilityButtons[i].onClick.AddListener(() => OnAbilityButton(idx)); }
        if (runButton != null) runButton.onClick.AddListener(OnRunPressed);
        if (captureOpenButton != null) captureOpenButton.onClick.AddListener(OnOpenCapturePanel);
        for (int i = 0; i < captureDeviceButtons.Length; i++) { int idx = i; captureDeviceButtons[i].onClick.AddListener(() => OnUseCaptureDevice(idx)); }

        UpdateCaptureDeviceCountsUI();
    }

    public void StartBattle(CreatureData wild, GameObject playerGO)
    {
        if (battleActive) return;
        battleActive = true;
        playerGameObjectRef = playerGO;
        var pc = playerGameObjectRef?.GetComponent<PlayerController>();
        if (pc != null) pc.enabled = false;

        if (PlayerRosterManager.Instance != null) playerCreature = PlayerRosterManager.Instance.GetActiveCreature();
        if (playerCreature == null)
        {
            playerCreature = new CreatureData { creatureName = CreatureNamer.GetName(Element.Fire, Rarity.Common), element = Element.Fire, rarity = Rarity.Common, level = 1, maxHP = 60, currentHP = 60, attack = 12, defense = 4 };
        }

        enemyCreature = wild;

        if (battlePanel != null) battlePanel.SetActive(true);

        SpawnBattleVisuals();

        UpdateUI();
        LogMessage($""A wild {enemyCreature.creatureName} appeared!"");
        playerTurn = true;
    }

    private void SpawnBattleVisuals()
    {
        if (VisualManager.Instance != null)
        {
            playerCreatureGO = VisualManager.Instance.CreateBattleVisual(playerCreature, null);
            enemyCreatureGO = VisualManager.Instance.CreateBattleVisual(enemyCreature, null);
            if (playerCreatureGO != null) playerCreatureGO.transform.position = battlePlayerPos.position;
            if (enemyCreatureGO != null) enemyCreatureGO.transform.position = battleEnemyPos.position;
        }
        else
        {
            if (creatureBattlePrefab == null)
            {
                creatureBattlePrefab = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                Destroy(creatureBattlePrefab.GetComponent<Collider>());
                creatureBattlePrefab.transform.localScale = Vector3.one * 1.2f;
            }
            if (playerCreatureGO != null) Destroy(playerCreatureGO);
            if (enemyCreatureGO != null) Destroy(enemyCreatureGO);
            playerCreatureGO = Instantiate(creatureBattlePrefab, battlePlayerPos.position, Quaternion.identity);
            enemyCreatureGO = Instantiate(creatureBattlePrefab, battleEnemyPos.position, Quaternion.identity);
            SetColorByElement(playerCreatureGO, playerCreature.element);
            SetColorByElement(enemyCreatureGO, enemyCreature.element);
        }

        if (playerCreatureGO != null) playerCreatureGO.transform.localScale *= (1f + GetScaleForRarity(playerCreature.rarity));
        if (enemyCreatureGO != null) enemyCreatureGO.transform.localScale *= (1f + GetScaleForRarity(enemyCreature.rarity));
    }

    private void SetColorByElement(GameObject go, Element e)
    {
        var rend = go.GetComponent<Renderer>();
        if (rend == null) return;
        switch (e)
        {
            case Element.Fire: rend.material.color = Color.red; break;
            case Element.Water: rend.material.color = Color.blue; break;
            case Element.Earth: rend.material.color = new Color(0.5f, 0.25f, 0.0f); break;
            case Element.Air: rend.material.color = Color.white; break;
            default: rend.material.color = Color.gray; break;
        }
    }

    private void UpdateUI()
    {
        string playerRarity = playerCreature != null ? $""[{playerCreature.rarity}]"" : """";
        string enemyRarity = enemyCreature != null ? $""[{enemyCreature.rarity}]"" : """";

        playerNameText.text = $""{playerCreature.creatureName} {playerRarity}  Lv{playerCreature.level}"";
        playerHPText.text = $""HP: {playerCreature.currentHP}/{playerCreature.maxHP}"";
        enemyNameText.text = $""{enemyCreature.creatureName} {enemyRarity}  Lv{enemyCreature.level}"";
        enemyHPText.text = $""HP: {enemyCreature.currentHP}/{enemyCreature.maxHP}"";

        for (int i = 0; i < abilityButtons.Length; i++)
        {
            if (i < playerCreature.abilities.Length)
            {
                abilityButtons[i].GetComponentInChildren<Text>().text = playerCreature.abilities[i].abilityName;
                abilityButtons[i].interactable = true;
            }
            else
            {
                abilityButtons[i].GetComponentInChildren<Text>().text = ""-"";
                abilityButtons[i].interactable = false;
            }
        }

        UpdateCaptureDeviceCountsUI();
    }

    public void OnAbilityButton(int index)
    {
        if (!playerTurn || !battleActive) return;
        if (index >= playerCreature.abilities.Length) return;
        StartCoroutine(PlayerUseAbility(index));
    }

    IEnumerator PlayerUseAbility(int index)
    {
        playerTurn = false;
        var a = playerCreature.abilities[index];
        LogMessage($""{playerCreature.creatureName} used {a.abilityName}!"");

        float eff = ElementalChart.GetEffectiveness(a.element, enemyCreature.element);
        int baseDamage = playerCreature.attack + a.power;
        int rawDamage = Mathf.RoundToInt(baseDamage * eff);
        int applied = Mathf.Max(1, rawDamage - enemyCreature.defense);
        enemyCreature.currentHP -= applied;

        string effText = eff > 1f ? ""It's super effective!"" : (eff < 1f ? ""It's not very effective..."" : """");
        LogMessage($""Dealt {applied} damage. {effText}"");

        UpdateUI();

        yield return new WaitForSeconds(0.8f);

        if (enemyCreature.currentHP <= 0) { EnemyFainted(); yield break; }

        StartCoroutine(EnemyTurn());
    }

    IEnumerator EnemyTurn()
    {
        LogMessage($""{enemyCreature.creatureName} is choosing an action..."");
        yield return new WaitForSeconds(0.8f);

        int idx = Random.Range(0, enemyCreature.abilities.Length);
        var a = enemyCreature.abilities[idx];
        LogMessage($""{enemyCreature.creatureName} used {a.abilityName}!"");

        float eff = ElementalChart.GetEffectiveness(a.element, playerCreature.element);
        int baseDamage = enemyCreature.attack + a.power;
        int rawDamage = Mathf.RoundToInt(baseDamage * eff);
        int applied = Mathf.Max(1, rawDamage - playerCreature.defense);
        playerCreature.currentHP -= applied;
        string effText = eff > 1f ? ""It's super effective!"" : (eff < 1f ? ""It's not very effective..."" : """");
        LogMessage($""It dealt {applied} damage. {effText}"");

        UpdateUI();

        yield return new WaitForSeconds(0.8f);

        if (playerCreature.currentHP <= 0) { PlayerFainted(); yield break; }

        playerTurn = true;
    }

    void EnemyFainted()
    {
        LogMessage($""The wild {enemyCreature.creatureName} fainted!"");
        int xp = enemyCreature.xpReward;
        LogMessage($""{playerCreature.creatureName} gained {xp} XP!"");
        playerCreature.level++;
        playerCreature.maxHP += 8;
        playerCreature.attack += 2;
        playerCreature.currentHP = playerCreature.maxHP;
        LogMessage($""{playerCreature.creatureName} leveled up to {playerCreature.level}!"");

        TryEvolvePlayerCreature();

        if (PlayerRosterManager.Instance != null) PlayerRosterManager.Instance.SetActiveCreature(playerCreature);
        SaveManager.Instance?.SaveGame();

        EndBattle(true);
    }

    void PlayerFainted()
    {
        LogMessage($""{playerCreature.creatureName} fainted..."");
        playerCreature.currentHP = Mathf.Max(1, playerCreature.maxHP / 2);
        EndBattle(false);
    }

    void EndBattle(bool playerWon)
    {
        StartCoroutine(EndBattleRoutine(playerWon));
    }

    IEnumerator EndBattleRoutine(bool playerWon)
    {
        yield return new WaitForSeconds(1f);

        if (playerCreatureGO != null) Destroy(playerCreatureGO);
        if (enemyCreatureGO != null) Destroy(enemyCreatureGO);

        if (battlePanel != null) battlePanel.SetActive(false);
        if (capturePanel != null) capturePanel.SetActive(false);

        if (playerGameObjectRef != null)
        {
            var pc = playerGameObjectRef.GetComponent<PlayerController>();
            if (pc != null) pc.enabled = true;
        }

        battleActive = false;
        LogMessage(""Battle ended."");
    }

    void OnRunPressed()
    {
        if (!battleActive) return;
        bool success = Random.value > 0.5f;
        if (success) { LogMessage(""Got away safely!""); EndBattle(false); }
        else { LogMessage(""Couldn't get away!""); StartCoroutine(EnemyTurn()); }
    }

    void LogMessage(string msg)
    {
        Debug.Log(msg);
        if (messageLogText != null) messageLogText.text = msg;
    }

    private void OnOpenCapturePanel()
    {
        if (!battleActive) return;
        if (capturePanel != null) { capturePanel.SetActive(!capturePanel.activeSelf); UpdateCaptureDeviceCountsUI(); }
    }

    private void OnUseCaptureDevice(int deviceIndex)
    {
        if (!battleActive) return;
        CaptureDeviceType dt = (CaptureDeviceType)deviceIndex;
        if (InventoryManager.Instance == null) { LogMessage(""No InventoryManager found.""); return; }
        int available = InventoryManager.Instance.GetCount(dt);
        if (available <= 0) { LogMessage($""No {dt} left!""); UpdateCaptureDeviceCountsUI(); return; }
        bool consumed = InventoryManager.Instance.UseDevice(dt);
        if (!consumed) { LogMessage(""Failed to use device.""); UpdateCaptureDeviceCountsUI(); return; }
        UpdateCaptureDeviceCountsUI();
        StartCoroutine(HandleCaptureAttempt(dt));
    }

    IEnumerator HandleCaptureAttempt(CaptureDeviceType device)
    {
        LogMessage($""You threw a {device}..."");
        yield return new WaitForSeconds(0.6f);

        if (device == CaptureDeviceType.MasterBall) { CaptureSuccess(); yield break; }

        float hpRatio = Mathf.Clamp01((float)enemyCreature.currentHP / Mathf.Max(1, enemyCreature.maxHP));
        float baseChance = (1f - hpRatio) * 0.6f + 0.05f;
        float rarityMultiplier = 1f;
        switch (enemyCreature.rarity)
        {
            case Rarity.Common: rarityMultiplier = 1.0f; break;
            case Rarity.Uncommon: rarityMultiplier = 0.8f; break;
            case Rarity.Rare: rarityMultiplier = 0.6f; break;
            case Rarity.Epic: rarityMultiplier = 0.4f; break;
            case Rarity.Legendary: rarityMultiplier = 0.25f; break;
        }

        float deviceModifier = 1f;
        switch (device)
        {
            case CaptureDeviceType.BasicBall: deviceModifier = 1.0f; break;
            case CaptureDeviceType.GreatBall: deviceModifier = 1.5f; break;
            case CaptureDeviceType.UltraBall: deviceModifier = 2.2f; break;
        }

        float finalChance = Mathf.Clamp(baseChance * deviceModifier * rarityMultiplier, 0.01f, 0.95f);
        float roll = Random.value;
        bool success = roll <= finalChance;

        LogMessage($""Capture roll: {roll:F2} <= {finalChance:F2} -> {(success ? ""Success"" : ""Fail"")}"");
        yield return new WaitForSeconds(0.6f);

        if (success) CaptureSuccess(); else CaptureFail();
    }

    void CaptureSuccess()
    {
        LogMessage($""Captured {enemyCreature.creatureName}!"");
        CreatureData captured = new CreatureData
        {
            creatureName = enemyCreature.creatureName,
            element = enemyCreature.element,
            level = enemyCreature.level,
            maxHP = enemyCreature.maxHP,
            currentHP = Mathf.Clamp(enemyCreature.currentHP, 1, enemyCreature.maxHP),
            attack = enemyCreature.attack,
            defense = enemyCreature.defense,
            abilities = enemyCreature.abilities,
            xpReward = enemyCreature.xpReward,
            rarity = enemyCreature.rarity,
            isCaptured = true,
            isProtected = enemyCreature.isProtected,
            isEvolved = enemyCreature.isEvolved,
            evolutionStage = enemyCreature.evolutionStage,
            nextEvolutionLevel = enemyCreature.nextEvolutionLevel
        };

        if (PlayerRosterManager.Instance != null)
        {
            bool addedToTeam = PlayerRosterManager.Instance.AddCreatureToTeamOrBox(captured);
            if (addedToTeam) LogMessage(""Added to your team!"");
            else LogMessage(""Your team is full — sent to box."");
        }

        if (enemyCreatureGO != null) Destroy(enemyCreatureGO);
        EndBattle(true);
        SaveManager.Instance?.SaveGame();
    }

    void CaptureFail()
    {
        LogMessage($""The {enemyCreature.creatureName} broke free!"");
        StartCoroutine(EnemyTurn());
    }

    void UpdateCaptureDeviceCountsUI()
    {
        if (captureDeviceCountTexts == null || InventoryManager.Instance == null) return;
        for (int i = 0; i < captureDeviceCountTexts.Length; i++)
        {
            CaptureDeviceType t = (CaptureDeviceType)i;
            int c = InventoryManager.Instance.GetCount(t);
            captureDeviceCountTexts[i].text = c.ToString();
        }
    }

    public CreatureData GetPlayerCreatureData() => playerCreature;
    public void SetPlayerCreatureData(CreatureData data)
    {
        if (data == null) return;
        playerCreature = data;
    }

    private float GetScaleForRarity(Rarity r)
    {
        switch (r)
        {
            case Rarity.Uncommon: return 0.06f;
            case Rarity.Rare: return 0.12f;
            case Rarity.Epic: return 0.22f;
            case Rarity.Legendary: return 0.35f;
            default: return 0f;
        }
    }

    void TryEvolvePlayerCreature()
    {
        if (playerCreature == null) return;
        if (playerCreature.rarity == Rarity.Legendary) return;
        if (playerCreature.isEvolved) return;
        if (playerCreature.nextEvolutionLevel <= 0) return;

        if (playerCreature.level >= playerCreature.nextEvolutionLevel)
        {
            bool evolved = EvolutionManager.ApplyEvolution(playerCreature);
            if (evolved)
            {
                LogMessage($""{playerCreature.creatureName} has evolved!"");
                UpdateUI();
            }
        }
    }
}
",

            // SaveManager.cs
            ["Scripts/SaveManager.cs"] = @"using System;
using System.IO;
using UnityEngine;

[DisallowMultipleComponent]
public class SaveManager : MonoBehaviour
{
    public static SaveManager Instance;
    private string saveFileName = ""savegame.json"";
    public string SaveFilePath => Path.Combine(Application.persistentDataPath, saveFileName);

    void Awake()
    {
        if (Instance == null) Instance = this;
        else { Destroy(gameObject); return; }
        DontDestroyOnLoad(gameObject);
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.F5)) SaveGame();
        if (Input.GetKeyDown(KeyCode.F9)) LoadGame();
        if (Input.GetKeyDown(KeyCode.Delete)) DeleteSave();
    }

    public bool HasSave() => File.Exists(SaveFilePath);

    public void SaveGame()
    {
        try
        {
            SaveData data = GatherSaveData();
            string json = JsonUtility.ToJson(data, true);
            File.WriteAllText(SaveFilePath, json);
            Debug.Log($""Game saved to: {SaveFilePath}"");
        }
        catch (Exception ex) { Debug.LogError($""Failed to save game: {ex}""); }
    }

    public bool LoadGame()
    {
        try
        {
            if (!HasSave()) { Debug.LogWarning(""No save file found.""); return false; }
            string json = File.ReadAllText(SaveFilePath);
            SaveData data = JsonUtility.FromJson<SaveData>(json);
            if (data == null) { Debug.LogError(""Failed to parse save file.""); return false; }
            ApplySaveData(data);
            Debug.Log(""Game loaded."");
            return true;
        }
        catch (Exception ex) { Debug.LogError($""Failed to load game: {ex}""); return false; }
    }

    public void DeleteSave()
    {
        try
        {
            if (HasSave()) { File.Delete(SaveFilePath); Debug.Log(""Save deleted.""); }
            else Debug.Log(""No save to delete."");
        }
        catch (Exception ex) { Debug.LogError($""Failed to delete save: {ex}""); }
    }

    SaveData GatherSaveData()
    {
        SaveData s = new SaveData();

        var player = FindObjectOfType<PlayerController>();
        s.playerPosition = new SerializableVector3(player != null ? player.transform.position : Vector3.zero);

        if (PlayerRosterManager.Instance != null)
        {
            s.team = PlayerRosterManager.Instance.GetTeamArray();
            s.box = PlayerRosterManager.Instance.GetBoxArray();
        }

        if (BattleSystem.Instance != null)
            s.playerCreature = BattleSystem.Instance.GetPlayerCreatureData();

        if (InventoryManager.Instance != null)
            s.inventory = InventoryManager.Instance.GetSaveArray();

        if (AreaManager.Instance != null)
        {
            s.visitedAreaIDs = AreaManager.Instance.GetVisitedAreaIDs();
            s.currentAreaID = AreaManager.Instance.CurrentAreaID;
        }

        if (QuestManager.Instance != null)
            s.questStates = QuestManager.Instance.GetQuestSaveStates();

        s.saveTime = DateTime.UtcNow.ToString(""o"");
        return s;
    }

    void ApplySaveData(SaveData data)
    {
        var player = FindObjectOfType<PlayerController>();
        if (player != null) player.Teleport(data.playerPosition.ToVector3());

        if (PlayerRosterManager.Instance != null)
            PlayerRosterManager.Instance.SetTeamAndBox(data.team, data.box);

        if (BattleSystem.Instance != null && data.playerCreature != null)
            BattleSystem.Instance.SetPlayerCreatureData(data.playerCreature);

        if (InventoryManager.Instance != null)
            InventoryManager.Instance.LoadFromSave(data.inventory);

        if (AreaManager.Instance != null)
        {
            AreaManager.Instance.SetVisitedAreas(data.visitedAreaIDs);
            if (data.currentAreaID >= 0)
            {
                Area a = AreaManager.Instance.GetAreaByID(data.currentAreaID);
                if (a != null) AreaManager.Instance.EnterArea(a);
            }
        }

        if (QuestManager.Instance != null)
            QuestManager.Instance.SetQuestSaveStates(data.questStates);
    }
}

[Serializable]
public class SaveData
{
    public SerializableVector3 playerPosition;
    public CreatureData playerCreature;
    public CreatureData[] team;
    public CreatureData[] box;
    public DeviceSaveData[] inventory;
    public int[] visitedAreaIDs;
    public int currentAreaID = -1;
    public QuestManager.QuestSaveState[] questStates;
    public string saveTime;
}

[Serializable]
public struct SerializableVector3
{
    public float x;
    public float y;
    public float z;
    public SerializableVector3(float rx, float ry, float rz) { x = rx; y = ry; z = rz; }
    public SerializableVector3(Vector3 v) { x = v.x; y = v.y; z = v.z; }
    public Vector3 ToVector3() => new Vector3(x, y, z);
}
",

            // AreaManager.cs (stub)
            ["Scripts/AreaManager.cs"] = @"using System.Collections.Generic;
using UnityEngine;

public class Area
{
    public int id;
    public string areaName;
}

public class AreaManager : MonoBehaviour
{
    public static AreaManager Instance;
    public int CurrentAreaID = -1;
    private HashSet<int> visited = new HashSet<int>();

    void Awake()
    {
        if (Instance == null) Instance = this;
        else { Destroy(gameObject); return; }
        DontDestroyOnLoad(gameObject);
    }

    public int[] GetVisitedAreaIDs() { var arr = new List<int>(visited); return arr.ToArray(); }
    public void SetVisitedAreas(int[] ids) { visited.Clear(); if (ids != null) foreach (var i in ids) visited.Add(i); }
    public Area GetAreaByID(int id) { return new Area { id = id, areaName = ""Area "" + id }; }
    public void EnterArea(Area a) { if (a != null) { CurrentAreaID = a.id; visited.Add(a.id); } }
}
",

            // PlayerController.cs (stub)
            ["Scripts/PlayerController.cs"] = @"using UnityEngine;

public class PlayerController : MonoBehaviour
{
    public void Teleport(Vector3 pos) { transform.position = pos; }
}
",

            // README.txt
            ["README.txt"] = @"GeneratedGamePackage
-------------------
This folder was generated by GenerateGamePackageEditor. It contains C# scripts for Unity:
- Creature system (spawning, naming, evolution)
- Roster and box management
- BattleSystem and capture logic
- QuestManager with Guardian's Pledge questline
- Visual system (VisualDatabase + VisualManager + CreatureVisual)
- SaveManager and InventoryManager
- Stubs for missing types so the code compiles quickly

How to use:
1. Import the package produced by this tool into any Unity project.
2. Create a VisualDatabase asset: Assets -> Create -> Visuals -> Visual Database and assign prefabs/thumbnails.
3. Add a GameObject 'Managers' and attach InventoryManager, SaveManager, PlayerRosterManager, QuestManager, VisualManager (assign db).
4. Hook up UI references on BattleSystem and RosterUI if you intend to use them.

You can expand, edit, and add more scripts to Assets/GeneratedGamePackage before exporting again.
"
        };

        // Write files
        foreach (var kv in files)
        {
            string fullPath = Path.Combine(Application.dataPath, "..", kv.Key).Replace('\\', '/');
            string dir = Path.GetDirectoryName(fullPath);
            if (!Directory.Exists(dir)) Directory.CreateDirectory(dir);
            File.WriteAllText(fullPath, kv.Value);
            Debug.Log("Wrote: " + kv.Key);
        }

        // Optionally create the VisualDatabase asset placeholder (can't create ScriptableObject easily without loading types),
        // but user will create it manually in Editor via Assets->Create->Visuals->Visual Database (script provides CreateAssetMenu).
    }
}
