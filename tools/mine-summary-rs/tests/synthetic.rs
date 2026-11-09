//! Runs the binary on a hand-built stream that holds one of each structure the summary reads, and checks the
//! output against `synthetic-expected.json`, which `tools/mine_summary.py`'s `summarise_save` wrote for the same
//! file (`tools_commit` aside). No real save is used.

use std::path::PathBuf;
use std::process::Command;

fn u32s(out: &mut Vec<u8>, v: u32) {
    out.extend_from_slice(&v.to_le_bytes());
}

fn string(out: &mut Vec<u8>, s: &str) {
    u32s(out, s.len() as u32);
    out.extend_from_slice(s.as_bytes());
}

/// Lua values: tag, payload.
fn lua_str(out: &mut Vec<u8>, s: &str) {
    u32s(out, 3);
    string(out, s);
}

fn lua_num(out: &mut Vec<u8>, x: f64) {
    u32s(out, 2);
    out.extend_from_slice(&x.to_le_bytes());
}

fn lua_bool(out: &mut Vec<u8>, b: bool) {
    u32s(out, 1);
    out.push(b as u8);
}

fn lua_table(out: &mut Vec<u8>, pairs: u32) {
    u32s(out, 4);
    out.push(1);
    u32s(out, pairs);
}

/// A script state: the path as a `str`, one byte, the pair count.
fn state(out: &mut Vec<u8>, path: &str, pairs: u32) {
    string(out, path);
    out.push(0);
    u32s(out, pairs);
}

fn instance(out: &mut Vec<u8>, id: u32, x: f32, y: f32) {
    u32s(out, id);
    let m = [
        0.6f32, 0.8, 0.0, 0.0, -0.8, 0.6, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, x, y, 3.0, 1.0,
    ];
    for f in m {
        out.extend_from_slice(&f.to_le_bytes());
    }
}

fn stream() -> Vec<u8> {
    let mut s = b"tf**".to_vec();
    for v in [604u32, 1900, 4096, 8192, 2_415_100] {
        u32s(&mut s, v);
    }
    s.extend_from_slice(&123_456i64.to_le_bytes()); // money
    u32s(&mut s, 7); // counter
    u32s(&mut s, 0); // info table
    u32s(&mut s, 1); // one mod
    for t in ["mod_a_1", "", "", "", ""] {
        string(&mut s, t);
    }
    u32s(&mut s, 0);
    s.push(0);
    u32s(&mut s, 0);
    u32s(&mut s, 0);
    u32s(&mut s, 0); // empty preview
    s.extend_from_slice(&[0; 6 * 8 + 11 * 4]);
    u32s(&mut s, 0); // pairs
    s.extend_from_slice(&[0; 2 * 4 + 9 * 8 + 2 * 4]);
    u32s(&mut s, 0); // labels
    s.extend_from_slice(&[0; 4 + 8 + 8 + 4]);
    u32s(&mut s, 0); // config mods
    u32s(&mut s, 2); // resources
    for t in [
        "climate",
        "::/climate/dry.clima",
        "nameList",
        "::/names/europe/europe.names",
    ] {
        string(&mut s, t);
    }
    u32s(&mut s, 1); // params: the settings
    string(&mut s, "");
    u32s(&mut s, 4);
    lua_str(&mut s, "isMapEditor");
    lua_bool(&mut s, false);
    lua_str(&mut s, "map");
    lua_table(&mut s, 2);
    lua_str(&mut s, "size");
    lua_num(&mut s, 3.0);
    lua_str(&mut s, "format");
    lua_num(&mut s, 2.0);
    lua_str(&mut s, "advancedOptions");
    lua_table(&mut s, 1);
    lua_str(&mut s, "cargoIncome");
    lua_num(&mut s, 2.5);
    lua_str(&mut s, "townConfig");
    lua_table(&mut s, 1);
    lua_str(&mut s, "sensitivityNoise");
    lua_num(&mut s, 9.0);
    string(&mut s, ""); // mission
    string(&mut s, ""); // kind
    s.push(0);
    u32s(&mut s, 601); // first version
    string(&mut s, "SyntheticS");

    // The model table: 101 animals, an industry, two vehicles.
    s.extend_from_slice(&[0xee; 8]);
    let mut paths: Vec<String> = (0..101).map(|i| format!("animal/a{i}.mdl")).collect();
    paths.push("industries/farm/farm_sm.mdl".into());
    paths.push("industries/farm/farm.mdl".into());
    paths.push("vehicle/truck/synthetic/synthetic_box.mdl".into());
    paths.push("vehicle/waggon/synthetic/synthetic_open.mdl".into());
    paths.push("vehicle/car/synthetic/synthetic_car.mdl".into());
    u32s(&mut s, paths.len() as u32);
    for (i, p) in paths.iter().enumerate() {
        string(
            &mut s,
            if i == paths.len() - 1 {
                "some_mod_1"
            } else {
                ""
            },
        );
        string(&mut s, p);
        u32s(&mut s, if i >= 103 { i as u32 + 40 } else { i as u32 });
    }
    s.extend_from_slice(&[0xee; 8]);

    // The cargo list: count, then source mod, path and id per entry.
    u32s(&mut s, 3);
    for (i, (src, path)) in [
        ("", "cargos/passengers/passengers.cargo"),
        ("", "cargos/fish/fish.cargo"),
        ("sugar_mod_1", "cargos/sugar.cargo"),
    ]
    .into_iter()
    .enumerate()
    {
        string(&mut s, src);
        string(&mut s, path);
        u32s(&mut s, i as u32);
    }
    s.extend_from_slice(&[0xee; 8]);

    // Script states.
    state(&mut s, "game_mechanics/company/company_progression.gs", 1);
    lua_str(&mut s, "companyState");
    lua_table(&mut s, 1);
    lua_num(&mut s, 1.0);
    lua_table(&mut s, 3);
    lua_str(&mut s, "potentialLevel");
    lua_num(&mut s, 3.0);
    lua_str(&mut s, "level");
    lua_num(&mut s, 2.0);
    lua_str(&mut s, "experience");
    lua_num(&mut s, 12.5);
    state(&mut s, "game_mechanics/company/company.gs", 1);
    lua_str(&mut s, "basePopulation");
    lua_num(&mut s, 1500.0);
    state(&mut s, "game_mechanics/achievements/achievements.gs", 5);
    lua_str(&mut s, "version");
    lua_num(&mut s, 2.0);
    lua_str(&mut s, "moneyEarned");
    lua_num(&mut s, 1e20);
    lua_str(&mut s, "averageSpeed");
    lua_num(&mut s, 0.00001);
    lua_str(&mut s, "vehiclesUsed");
    lua_table(&mut s, 3);
    lua_num(&mut s, 1.0);
    lua_bool(&mut s, true);
    lua_bool(&mut s, true); // the same key as 1
    lua_bool(&mut s, true);
    lua_str(&mut s, "x");
    lua_bool(&mut s, true);
    lua_str(&mut s, "flag");
    lua_bool(&mut s, true);
    state(&mut s, "game_mechanics/game_time/game_time.gs", 2);
    lua_str(&mut s, "timeOfDayMode");
    lua_str(&mut s, "Automatic");
    lua_str(&mut s, "weatherMode");
    lua_str(&mut s, "Dynamic");
    state(&mut s, "game_mechanics/subventions/subventions.gs", 1);
    lua_str(&mut s, "activeSubventions");
    lua_table(&mut s, 1);
    lua_num(&mut s, 4.0);
    lua_num(&mut s, 5.0);
    state(&mut s, "game_mechanics/towns/town.gs", 1);
    lua_str(&mut s, "townStates");
    lua_table(&mut s, 0);
    s.extend_from_slice(&[0xee; 8]);

    // The game speed component and a day table of three days.
    s.extend_from_slice(&[9, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]);
    u32s(&mut s, 2000);
    u32s(&mut s, 2);
    s.extend_from_slice(&[0; 8]);
    s.extend_from_slice(&[1, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]);
    s.extend_from_slice(&5000u64.to_le_bytes());
    s.push(1);
    s.extend_from_slice(&4600u64.to_le_bytes());
    u32s(&mut s, 3);
    for (t, d) in [(0u64, 2_415_021u32), (2000, 2_415_022), (4000, 2_415_023)] {
        s.extend_from_slice(&t.to_le_bytes());
        u32s(&mut s, d);
    }
    s.extend_from_slice(&[0xee; 8]);

    // The town array's header (first word, type 27, no free row, two rows), then two town records 78 bytes apart.
    for w in [12288u32, 27, 0, 2] {
        u32s(&mut s, w);
    }
    for (caps, f) in [([100u32, 200, 300], 1.0f32), ([10, 20, 30], 1.5)] {
        let at = s.len();
        for c in caps {
            u32s(&mut s, c);
        }
        for _ in 0..4 {
            s.extend_from_slice(&f.to_le_bytes());
        }
        s.extend_from_slice(&[0; 5]);
        u32s(&mut s, 1);
        u32s(&mut s, 1); // commercial: fish
        s.extend_from_slice(&[0x11; 4]);
        u32s(&mut s, 1);
        u32s(&mut s, 2); // industrial: sugar
        s.resize(at + 78, 0x22);
    }
    s.extend_from_slice(&[0xee; 8]);

    // The entity names table: its type (16), a free list of one slot (5) and the count, then the names.
    for w in [16u32, 1, 5, 6] {
        u32s(&mut s, w);
    }
    for n in [
        "<name> Transport",
        "Alpha",
        "Beta",
        "no name",
        "Alpha Station",
        "Beta-Nord Farm",
    ] {
        string(&mut s, n);
    }
    s.extend_from_slice(&[0xff; 8]);

    // The edge-addon name table's end and the journal after it.
    s.extend_from_slice(b"edge_addons/barrier_track_b.edge");
    u32s(&mut s, 5);
    u32s(&mut s, 0xffff_ffff);
    u32s(&mut s, 1); // one id
    u32s(&mut s, 77);
    u32s(&mut s, 0xffff_ffff);
    s.extend_from_slice(&[1, 0, 0, 0, 0]);
    u32s(&mut s, 3);
    for (t, a, ty) in [
        (0i64, 100_000i64, 0u8),
        (1_000, -5_000, 2),
        (3 * 1_461_000 + 5, 28_456, 5),
    ] {
        s.extend_from_slice(&t.to_le_bytes());
        s.extend_from_slice(&a.to_le_bytes());
        s.extend_from_slice(&[ty, 0, 0, 0, 0]);
    }
    s.extend_from_slice(&123_456i64.to_le_bytes());
    s.extend_from_slice(&[0xee; 8]);

    // Instances: the farm twice, a truck, two wagons, a car, and one with an id outside the table.
    for (id, x) in [
        (101u32, 10.0f32),
        (101, 20.0),
        (143, 30.0),
        (144, 40.0),
        (144, 50.0),
        (145, 60.0),
        (9999, 70.0),
    ] {
        instance(&mut s, id, x, -x);
        s.extend_from_slice(&[0x33; 3]);
    }
    s.extend_from_slice(&[0xee; 16]);

    // Two building records: town entity 1 on parcel entity 4, town 2 on parcel 5.
    for (town, parcel) in [(1u32, 4u32), (2, 5)] {
        for w in [500u32, 500, 1, 0] {
            u32s(&mut s, w);
        }
        s.push(0);
        u32s(&mut s, 1);
        u32s(&mut s, parcel);
        u32s(&mut s, 1);
        s.extend_from_slice(&10.0f32.to_le_bytes());
        u32s(&mut s, town);
        s.extend_from_slice(&0u64.to_le_bytes());
    }
    s.extend_from_slice(&[0xee; 8]);

    // The parcel table: two parcels, the first with four faces (centre 100, 200), the second with one (-50.5, 30.25).
    u32s(&mut s, 2);
    for (faces, cx, cy) in [(4u32, 100.0f32, 200.0f32), (1, -50.5, 30.25)] {
        u32s(&mut s, 7);
        s.push(1);
        s.extend_from_slice(&0.5f32.to_le_bytes());
        u32s(&mut s, faces);
        for _ in 0..faces {
            u32s(&mut s, 4);
            for (dx, dy) in [(-4.0f32, -4.0f32), (4.0, -4.0), (4.0, 4.0), (-4.0, 4.0)] {
                for v in [cx + dx, cy + dy, 0.0] {
                    s.extend_from_slice(&v.to_le_bytes());
                }
            }
            u32s(&mut s, 1);
        }
        s.extend_from_slice(&8.0f32.to_le_bytes());
    }
    s.extend_from_slice(&[0xee; 8]);

    // The entity table: the company, two towns, a free id, two parcels, a line and a named station, then free
    // entries up to 1,000, the count again and the trailer.
    let ents: [&[(u32, u32)]; 8] = [
        &[(0, 0), (16, 0)],
        &[(27, 0), (16, 1), (0, 1), (10, 0)],
        &[(27, 1), (16, 2), (0, 2), (10, 1)],
        &[(0xffff_ffff, 0xffff_ffff)],
        &[(34, 0x4000_0000)],
        &[(34, 0x4000_0001)],
        &[(10, 2), (16, 3), (17, 0), (18, 0), (72, 0), (75, 0)],
        &[(16, 4), (0, 3)],
    ];
    u32s(&mut s, 1000);
    for i in 0..1000 {
        let e: &[(u32, u32)] = ents
            .get(i)
            .copied()
            .unwrap_or(&[(0xffff_ffff, 0xffff_ffff)]);
        u32s(&mut s, e.len() as u32);
        for &(t, slot) in e {
            u32s(&mut s, t);
            u32s(&mut s, slot);
        }
    }
    u32s(&mut s, 1000);
    for w in [1u32, 1, 0, 1, 1, 0, 1] {
        u32s(&mut s, w);
    }
    s.extend_from_slice(&[0xee; 16]);
    s
}

#[test]
fn the_synthetic_stream_gives_the_python_summary() {
    let dir = std::env::temp_dir().join(format!("mine-summary-test-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    let path: PathBuf = dir.join("synthetic.tf3");
    let mut file = zstd::encode_all(&stream()[..], 3).unwrap();
    file.extend_from_slice(&[0x28, 0xb5, 0x2f, 0xfd, 0x20, 0x00, 0x01, 0x00, 0x00]);
    std::fs::write(&path, &file).unwrap();
    if let Some(keep) = std::env::var_os("MINE_SUMMARY_KEEP_SYNTHETIC") {
        std::fs::copy(&path, keep).unwrap();
    }
    let out = Command::new(env!("CARGO_BIN_EXE_mine-summary"))
        .arg(&path)
        .args(["--game", dir.join("no-install").to_str().unwrap()])
        .output()
        .unwrap();
    std::fs::remove_dir_all(&dir).unwrap();
    assert!(out.status.success());
    let text = String::from_utf8(out.stdout).unwrap();
    let strip = |t: &str| -> String {
        t.lines()
            .filter(|l| !l.trim_start().starts_with("\"tools_commit\""))
            .collect::<Vec<_>>()
            .join("\n")
    };
    let expected = include_str!("synthetic-expected.json");
    assert_eq!(strip(&text), strip(expected));
}
