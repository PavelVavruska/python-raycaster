cd pyext-rustlib/
cargo build --release
cd ..
cp pyext-rustlib/target/release/librustlib.so mathematics/raycasting/rustlib.so