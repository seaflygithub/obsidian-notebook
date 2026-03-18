[TOC]

# 开发环境部署





# 所有权

- 所有的程序都必须和计算机内存打交道，如何从内存中申请空间来存放程序的运行内容，如何在不需要的时候释放这些空间，成了重中之重，也是所有编程语言设计的难点之一。在计算机语言不断演变过程中，出现了三种流派：
  - **垃圾回收**：在程序运行时不断寻找不再使用的内存，典型代表：Java、Go。
  - **手动管理内存**：在程序中，通过函数调用的方式来申请和释放内存，典型代表：C/C++。
  - **通过所有权来管理内存**：编译器在编译时会根据一系列规则进行检查。

---

其中 Rust 选择了第三种，最妙的是，这种**检查只发生在编译期**，因此对于程序运行期，不会有任何性能上的损失。由于所有权是一个新概念，因此读者需要花费一些时间来掌握它，一旦掌握，海阔天空任你飞跃。

## 堆和栈

- 在很多语言中，你并不需要深入了解栈与堆。 但对于 Rust 这样的系统编程语言，值是位于栈上还是堆上非常重要，因为这会影响程序的行为和性能。栈和堆的核心目标就是为程序在运行时提供可供使用的内存空间。打个现实比方，相当于栈就是在很大的一间教室里，给你分配临时几个座位供你使用，用完之后这几个作为就不属于你了，而堆则是你使用完之后，你还能转交给其他人使用。
- 由于后进先出的特性，栈中的所有数据都必须占用**已知且固定大小的内存空间**，假设数据大小是未知的，那么在取出数据时，你将无法取到你想要的数据。

---

- 而对于堆，操作系统在堆的某处找到一块足够大的空位，把它标记为已使用，并**返回一个表示该位置地址的指针**，**接着，该指针会被推入栈中**，因为指针的大小是已知且固定的，在后续使用过程中，你将通过栈中的指针，来获取数据在堆上的实际内存位置，进而访问该数据。由上可知，堆是一种缺乏组织的数据结构。想象一下去餐馆就座吃饭：进入餐馆，告知服务员有几个人，然后服务员找到一个够大的空桌子（堆上分配的内存空间）并领你们过去。如果有人来迟了，他们也可以通过桌号（栈上的指针）来找到你们坐在哪。
- 在栈上分配内存比在堆上分配内存要快，因为入栈时操作系统无需进行函数调用（或更慢的系统调用）来分配新的空间，只需要将新数据放入栈顶即可。相比之下，在堆上分配内存则需要更多的工作，这是因为操作系统必须首先找到一块足够存放数据的内存空间，接着做一些记录为下一次分配做准备，如果当前进程分配的内存页不足时，还需要进行系统调用来申请更多内存。 因此，处理器在栈上分配数据会比在堆上分配数据更加高效。
- 当你的代码调用一个函数时，传递给函数的参数（包括可能指向堆上数据的指针和函数的局部变量）依次被压入栈中，当函数调用结束时，这些值将被从栈中按照相反的顺序依次移除。因为堆上的数据缺乏组织，因此跟踪这些数据何时分配和释放是非常重要的，否则堆上的数据将产生内存泄漏 —— 这些数据将永远无法被回收。这就是 Rust 所有权系统为我们提供的强大保障。虽然对于其他很多编程语言，你确实无需理解堆栈的原理，但是在 Rust 中，**明白堆栈的原理，对于我们理解所有权的工作原理会有很大的帮助**。

## 所有权规则

- 所有权的规则，首先请谨记以下规则：
  - Rust 中每一个 **<font color=red>值</font>** 都被一个 **<font color=red>变量</font>** 所拥有，该变量被称为值的所有者；
  - 一个值同时只能被一个变量所拥有；
  - 当所有者（变量）离开作用域范围时，这个值将被丢弃(drop)。

---

```rust
{
    let s1 = String::from("hello");
    let s2 = s1;
}
```
- 如上代码所示，当变量离开作用域后，Rust 会自动调用 drop 函数并清理变量的堆内存。不过由于两个 String 变量指向了同一位置。这就有了一个问题：当 s1 和 s2 离开作用域，它们都会尝试**释放相同的内存**。

---

```rust
{
    let x1 = 5;   //声明变量x1,是栈的push操作
    let x2 = x1;  //声明变量x2,是栈的push操作
}
//离开作用域之后,x1会被drop释放,这里只有栈的pop操作
//离开作用域之后,x2会被drop释放,这里只有栈的pop操作

{
    let s1 = String::from("hello");
    let s2 = s1;
}
//离开作用域之后,s1会被drop释放,除了栈的pop操作,还有该复杂类型自己的drop操作会被自动调用
//离开作用域之后,s2会被drop释放,除了栈的pop操作,还有该复杂类型自己的drop操作会被自动调用
```

- 因此，Rust 这样解决问题：当 s1 被赋予 s2 后，Rust 认为 s1 不再有效，因此也无需在 s1 离开作用域后 drop 任何东西，这就是把所有权从 s1 转移给了 s2，s1 在被赋予 s2 后就马上失效了。

---

- 这里用C++代码来验证它被drop两次的现象：
```cpp{.line-numbers}
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <iostream>
using namespace std;

class mystring {
public:
	mystring()
	{
		str = (char *)malloc(8);
		len = 8;
	}
	~mystring()
	{
        //这个位置会打印信息表示drop被调用
		printf("varstack=0x%x, will free (str=0x%x)\n", this, str);
		if (str)
		{
			//free(str);
			str = NULL;
			len = 0;
		}
	}
	char *fromstr(const char *instr)
	{
		len = strlen(instr) + 1;
		str = (char *)realloc(str, len);
		strncpy(str, instr, len-1);
		return str;
	}
	
private:
	char *str;
	unsigned int len;
	unsigned int maxlen;
};

int main()
{
	{
		mystring str1;
		mystring str2 = str1;
		char *str = str1.fromstr("hello world!");
		printf("str1 = %s\n", str);
	}
    //此时str1和str2都离开作用域了,因此它们的析构函数都会被调用

	return 0;
}
```

- 下面是代码运行效果：
```cpp
str1 = hello world!
varstack=0x50c285c0, will free (str=0x1732e70)
varstack=0x50c285d0, will free (str=0x1732e70)  同一个地址(str)被释放两次。。。

而rust在上面 str2=str1 赋值时，就直接让str1失效了，这很关键！！！
```

## 浅拷贝

![[image_20241110101002.png]]

- 下面是浅拷贝的实验代码，下面代码无法访问user1的值了；
- 基本类型的浅拷贝是rust默认已经实现了copy trait，而复合类型，则需要自己实现copy trait。

```rust
#[derive(Debug)]

struct User {
    active: bool,
    sex: u32, //1=femal, 0=male
    sign_in_count: u64,
}

fn main()
{
    let user1 = User {
        //rust不是不让浅拷贝那种带堆分配的复杂类型么
        //那我们用这种不带任何堆分配相关的成员,来做浅拷贝赋值实验
        sex: 1,
        active: true,
        sign_in_count: 1,
    };
    let user2 = user1;

    println!("{:#?}", user1); //无法访问
    println!("{:#?}", user2);
    //dbg!(user2);//need #[derive(Debug)]
}
```

---

![[image_20241127064910.png]]

---

## 复合类型默认没有实现浅拷贝

- 用println直接打印打印结构体，会报错：
`println!("user1 is {}", user1);`
error[E0277]: `User` doesn't implement `std::fmt::Display`

- 使用dbg宏来打印结构体值：
`println!("user1 is {:?}", user1);`
error[E0277]: `User` doesn't implement `Debug`
= help: the trait `Debug` is not implemented for `User`
= note: add `#[derive(Debug)]` to `User` or manually `impl Debug for User`


## 复合类型

- 结构体
- 字符串与切片：`[开始索引..终止索引]`，左闭右开区间`[idxA..idxB)`。

- 在对字符串使用切片语法时需要格外小心，切片的索引必须落在字符之间的边界位置，也就是 UTF-8 字符的边界，例如中文在 UTF-8 中占用三个字节，下面的代码就会崩溃：
```rust
fn main()
{
    let s = "中国人";
    let a = &s[0..2];
    println!("{}",a);
}
```

PS C:\Users\P15\Desktop\hellorust> cargo run
   Compiling hello v0.1.0 (C:\Users\P15\Desktop\hellorust)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.21s
     Running `target\debug\hello.exe`
thread 'main' panicked at src/main.rs:6:15:
**byte index 2 is not a char boundary**; it is inside '中' (bytes 0..3) of `中国人`
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
error: process didn't exit successfully: `target\debug\hello.exe` (exit code: 101)

---

- 因为切片是对集合的部分引用，因此不仅仅字符串有切片，其它集合类型也有，例如数组：
```rust
let a = [1, 2, 3, 4, 5];

let slice = &a[1..3];
```

---

- Rust 在语言级别，只有一种字符串类型： str，它通常是以引用类型出现 &str，也就是上文提到的字符串切片。虽然语言级别只有上述的 str 类型，但是在标准库里，还有多种不同用途的字符串类型，其中使用最广的即是 String 类型。
`let s: &str = "Hello, world!";`

- 除了 String 类型的字符串，Rust 的标准库还提供了其他类型的字符串，例如 OsString， OsStr， CsString 和 CsStr 等，注意到这些名字都以 String 或者 Str 结尾了吗？它们分别对应的是具有所有权和被借用的变量。

---

- 在其它语言中，使用索引的方式访问字符串的某个字符或者子串是很正常的行为，但是在 Rust 中就会报错：
```rust
   let s1 = String::from("hello");
   let h = s1[0];
```

- 字符串的底层的数据存储格式实际上是[ u8 ]，一个字节数组。对于 let hello = String::from("Hola"); 这行代码来说，Hola 的长度是 4 个字节，因为 "Hola" 中的每个字母在 UTF-8 编码中仅占用 1 个字节，但是对于下面的代码呢？（里面是内容是中文，那么索引可能就不在中文字符边界上）。
`let hello = String::from("中国人");`

- 如果问你该字符串多长，你可能会说 3，但是实际上是 9 个字节的长度，因为大部分常用汉字在 UTF-8 中的长度是 3 个字节，因此这种情况下对 hello 进行索引，访问 &hello[0] 没有任何意义，因为你取不到 中 这个字符，而是取到了这个字符三个字节中的第一个字节，这是一个非常奇怪而且难以理解的返回值。

---

## String的其他操作


- 追加: push
```rust
fn main() {
    let mut s = String::from("Hello ");

    s.push_str("rust");
    println!("追加字符串 push_str() -> {}", s);

    s.push('!');
    println!("追加字符 push() -> {}", s);
}
```

```txt
运行效果: 
追加字符串 push_str() -> Hello rust
追加字符 push() -> Hello rust!
```

---

- 插入: insert
```rust
fn main() {
    let mut s = String::from("Hello rust!");
    s.insert(5, ',');
    println!("插入字符 insert() -> {}", s);
    s.insert_str(6, " I like");
    println!("插入字符串 insert_str() -> {}", s);
}
```

```txt
运行效果: 
插入字符 insert() -> Hello, rust!
插入字符串 insert_str() -> Hello, I like rust!
```

---

- 替换: replace
- 接收两个参数，第一个参数是要被替换的字符串，第二个参数是新的字符串。该方法会替换所有匹配到的字符串。该方法是返回一个**新的字符串**，而不是操作原来的字符串。
```rust
fn main() {
    let oldstr1 = String::from("I like rust. Learning rust is my favorite!");
    let newstr1 = oldstr1.replace("rust", "RUST");
    dbg!(newstr1);
}
//new_string_replace = "I like RUST. Learning RUST is my favorite!"
```

---

- 替换: replacen
- 接收三个参数，前两个参数与 replace() 方法一样，第三个参数则表示替换的个数。该方法是返回一个新的字符串，而不是操作原来的字符串。
```rust
fn main() {
    let string_replace = "I like rust. Learning rust is my favorite!";
    let new_string_replacen = string_replace.replacen("rust", "RUST", 1);
    dbg!(new_string_replacen);
}
//new_string_replacen = "I like RUST. Learning rust is my favorite!"
```

---

- replace_range, 接收两个参数，第一个参数是要替换字符串的范围（Range），第二个参数是新的字符串。该方法是直接操作原来的字符串，**不会返回新的字符串**。该方法需要使用 mut 关键字修饰。
```rust
fn main() {
    let mut string_replace_range = String::from("I like rust!");
    string_replace_range.replace_range(7..8, "R");
    dbg!(string_replace_range);
}
//string_replace_range = "I like Rust!"
```

---

- 与字符串删除相关的方法有 4 个，它们分别是 pop()，remove()，truncate()，clear()。这四个方法仅适用于 String 类型。

- pop —— 删除并返回字符串的最后一个字符，即返回这个被删除的字符。该方法是直接操作原来的字符串。但是存在返回值，其返回值是一个 Option 类型，如果字符串为空，则返回 None。

- **remove** —— 删除并返回字符串中指定位置的字符
```rust
    // 删除第一个汉字
    string_remove.remove(0);
```

- truncate —— 删除字符串中从指定位置开始到结尾的全部字符
```rust

fn main() {
    let mut string_truncate = String::from("测试truncate");
    string_truncate.truncate(3);
    dbg!(string_truncate);
}
//删掉了除【测】之后的所有字符
```

- clear —— 清空字符串，该方法是直接操作原来的字符串。调用后，删除字符串中的所有字符，相当于 truncate() 方法参数为 0 的时候。

---

- 字符串连接(concatenate)

```rust
fn main() {
    let s1 = String::from("hello,");
    let s2 = String::from("world!");
    // 在下句中，s1的所有权被转移走了，因此后面不能再使用s1
    let s3 = s1 + &s2;
    assert_eq!(s3,"hello,world!");
    // 下面的语句如果去掉注释，就会报错
    // println!("{}",s1);
}
```

- 使用 format! 连接字符串
```rust
fn main() {
    let s1 = "hello";
    let s2 = String::from("rust");
    let s = format!("{} {}!", s1, s2);
    println!("{}", s);
}
```


## 操作UTF-8字符串

- 操作字符：
```rust
for c in "中国人".chars() {
    println!("{}", c);
}
//中
//国
//人
```

---

- 操作字节：这种方式是返回字符串的底层字节数组表现形式：
```rust
for b in "中国人".bytes() {
    println!("{}", b);
}
```

- 输出如下：
```txt
228
184
173
229
155
189
228
186
186
```

---

- 获取子串，要准确的从 UTF-8 字符串中获取子串是较为复杂的事情，这种变长的字符串中取出某一个子串，使用标准库你是做不到的。 你需要在 crates.io 上搜索 utf8 来寻找想要的功能。可以考虑尝试下这个库：`utf8_slice`。


## 元组

- 元组的好处就是，可以使用元组返回多个值。
- 元组是由多种类型组合到一起形成的，因此它是复合类型，元组的长度是固定的，元组中元素的顺序也是固定的。
- 可以使用模式匹配或者 . 操作符来获取元组中的值。
```rust{.line-numbers}
fn main() {
    let tup = (500, 6.4, 1);

    let (x, y, z) = tup;

    //用模式匹配解构元组
    println!("The value of y is: {}", y);
}

fn main() {
    let x: (i32, f64, u8) = (500, 6.4, 1);

    let five_hundred = x.0;

    let six_point_four = x.1;

    //用点的方式来访问元组中的值
    let one = x.2;
}
```

## 结构体与方法

```rust{.line-numbers}
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

// Circle的方法，&self表示借用当前的Circle结构体
/*
需要注意的是，self 依然有所有权的概念
    self 表示 Rectangle 的所有权转移到该方法中，这种形式用的较少
    &self 表示该方法对 Rectangle 的不可变借用
    &mut self 表示可变借用
 */
impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }
}

fn main() {
    let rect1 = Rectangle { width: 30, height: 50 };

    // println!("{:#?}", rect);
    // println!("s = {}", s);
    // dbg!(rect);

    println!(
        "The area of the rectangle is {} square pixels.",
        rect1.area()
    );
}
```

- 在 Rust 中，允许方法名跟结构体的字段名相同：当我们使用 rect1.width() 时，Rust 知道我们调用的是它的方法，如果使用 rect1.width，则是访问它的字段。一般来说，方法跟字段同名，往往适用于实现 getter 访问器，例如:

```rust{.line-numbers}
mod my {
    pub struct Rectangle {
        width: u32,
        pub height: u32,
    }

    impl Rectangle {
        pub fn new(width: u32, height: u32) -> Self {
            Rectangle { width, height }
        }
        pub fn width(&self) -> u32 {
            return self.width;
        }
        pub fn height(&self) -> u32 {
            return self.height;
        }
    }
}

fn main() {
    let rect1 = my::Rectangle::new(30, 50);

    println!("{}", rect1.width()); // OK
    println!("{}", rect1.height()); // OK
    // println!("{}", rect1.width); // Error - the visibility of field defaults to private
    println!("{}", rect1.height); // OK
}
```

---

- 方法和函数一样，可以使用多个参数：
```rust{.line-numbers}
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
}

fn main() {
    let rect1 = Rectangle { width: 30, height: 50 };
    let rect2 = Rectangle { width: 10, height: 40 };
    let rect3 = Rectangle { width: 60, height: 45 };

    println!("Can rect1 hold rect2? {}", rect1.can_hold(&rect2));
    println!("Can rect1 hold rect3? {}", rect1.can_hold(&rect3));
}
```

---

- 现在大家可以思考一个问题，如何为一个结构体定义一个构造器方法？也就是接受几个参数，然后构造并返回该结构体的实例。其实答案在开头的代码片段中就给出了，很简单，参数中不包含 self 即可。
- 这种定义在 impl 中且没有 self 的函数被称之为关联函数： 因为它没有 self，不能用 f.read() 的形式调用，因此它是一个函数而不是方法，它又在 impl 中，与结构体紧密关联，因此称为**关联函数**。在之前的代码中，我们已经多次使用过关联函数，例如 **String::from**，用于创建一个动态字符串。因为是函数，所以不能用 . 的方式来调用，我们需要用 :: 来调用，例如 `let sq = Rectangle::new(3, 3);`。这个方法位于结构体的命名空间中：:: 语法用于关联函数和模块创建的命名空间。
```rust
impl Rectangle {
    fn new(w: u32, h: u32) -> Rectangle {
        Rectangle { width: w, height: h }
    }
}
```


## 生命周期

```rust
fn main() {
    let string1 = String::from("abcd");
    let string2 = "xyz";

    let result = longest(string1.as_str(), &string2);
    println!("The longest string is {}", result);
}

fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        return x;
    } else {
        return y;
    }
}
```



## 泛型Generics

- 我们在编程中，经常有这样的需求：用同一功能的函数处理不同类型的数据，例如两个数的加法，无论是整数还是浮点数，甚至是自定义类型，都能进行支持。在不支持泛型的编程语言中，通常需要为每一种类型编写一个函数。

---

- 在编程的时候，我们经常利用多态。通俗的讲，多态就是好比坦克的炮管，既可以发射普通弹药，也可以发射制导炮弹（导弹），也可以发射贫铀穿甲弹，甚至发射子母弹，没有必要为每一种炮弹都在坦克上分别安装一个专用炮管，即使生产商愿意，炮手也不愿意，累死人啊。所以在编程开发中，我们也需要这样“通用的炮管”，这个“通用的炮管”就是多态。

```rust
fn add<T>(a:T, b:T) -> T {
    a + b
}

fn main() {
    println!("add i8: {}", add(2i8, 3i8));
    println!("add i32: {}", add(20, 30));
    println!("add f64: {}", add(1.23, 1.23));
}
```

---

- 结构体使用泛型, 下面代码定义了一个坐标点 Point，它可以存放任何类型的坐标值：
```rust{.line-numbers}
struct Point<T> {
    x: T,
    y: T,
}

fn main() {
    let integer = Point { x: 5, y: 10 };
    let float = Point { x: 1.0, y: 4.0 };
}
```

---

- 这个枚举和 Option 一样，主要用于函数返回值，与 **Option 用于值的存在与否**不同，Result 关注的主要是**值的正确性**。
```rust
enum Option<T> {
    Some(T),
    None,
}

enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

- 如果函数正常运行，则最后返回一个 Ok(T)，T 是函数具体的返回值类型，如果函数异常运行，则返回一个 Err(E)，E 是错误类型。例如打开一个文件：如果成功打开文件，则返回 Ok(std::fs::File)，因此 T 对应的是 std::fs::File 类型；而当打开文件时出现问题时，返回 Err(std::io::Error)，E 对应的就是 std::io::Error 类型。

---

- 方法中使用泛型
```rust{.line-numbers}
struct Point<T> {
    x: T,
    y: T,
}

impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}

fn main() {
    let p = Point { x: 5, y: 10 };

    println!("p.x = {}", p.x());
}
```


---

- 除了结构体中的泛型参数，我们还能在该结构体的方法中定义额外的泛型参数，就跟泛型函数一样：
```rust
struct Point<T, U> {
    x: T,
    y: U,
}
```

---

- 为具体的泛型类型实现方法：对于 `Point<T>` 类型，你不仅能定义基于 T 的方法，还能针对特定的具体类型，进行方法定义：
```rust
impl Point<f32> {
    fn distance_from_origin(&self) -> f32 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}
```

- 这段代码意味着 Point<f32> 类型会有一个方法 distance_from_origin，而其他 T 不是 f32 类型的 Point<T> 实例则没有定义此方法。这个方法计算点实例与坐标(0.0, 0.0) 之间的距离，并使用了只能用于浮点型的数学运算符。


---

- **const泛型**：我们定义了一个类型为 [T; N] 的数组，其中 T 是一个基于类型的泛型参数，这个和之前讲的泛型没有区别，而重点在于 N 这个泛型参数，它是一个基于值的泛型参数！因为它用来替代的是数组的长度。
```rust{.line-numbers}
fn display_array<T: std::fmt::Debug, const N: usize>(arr: [T; N]) {
    println!("{:?}", arr);
}
fn main() {
    let arr: [i32; 16] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16];
    display_array(arr);

    let arr: [i32; 2] = [1, 2];
    display_array(arr);
}
```


---

- **const函数**：通常情况下，函数是在运行时被调用和执行的。然而，在某些场景下，我们希望在编译期就计算出一些值，以提高运行时的性能或满足某些编译期的约束条件。例如，定义数组的长度、计算常量值等。有了 const fn，我们可以在编译期执行这些函数，从而将计算结果直接嵌入到生成的代码中。这不仅以高了运行时的性能，还使代码更加简洁和安全。要定义一个常量函数，只需要在函数声明前加上 const 关键字。例如：
```rust{.line-numbers}
const fn add(a: usize, b: usize) -> usize {
    a + b
}

const RESULT: usize = add(5, 10);

fn main() {
    println!("The result is: {}", RESULT);
}
```

- 将 const fn 与 const 泛型 结合，可以实现更加灵活和高效的代码设计。例如，创建一个固定大小的缓冲区结构，其中缓冲区大小由编译期计算确定：
```rust{.line-numbers}
struct Buffer<const N: usize> {
    data: [u8; N],
}

const fn compute_buffer_size(factor: usize) -> usize {
    factor * 1024
}

fn main() {
    const SIZE: usize = compute_buffer_size(4);
    let buffer = Buffer::<SIZE> {
        data: [0; SIZE],
    };
    println!("Buffer size: {} bytes", buffer.data.len());
}
```

---

- 让我们看看一个使用标准库中 Option 枚举的例子：
```rust
let integer = Some(5);
let float = Some(5.0);
```

- 编译器生成的单态化版本的代码看起来像这样：
```rust
enum Option_i32 {
    Some(i32),
    None,
}

enum Option_f64 {
    Some(f64),
    None,
}

fn main() {
    let integer = Option_i32::Some(5);
    let float = Option_f64::Some(5.0);
}
```

- 我们可以使用泛型来编写不重复的代码，而 Rust 将会为每一个实例编译其特定类型的代码。这意味着在使用泛型时没有运行时开销；当代码运行，它的执行效率就跟好像手写每个具体定义的重复代码一样。这个单态化过程正是 Rust 泛型在运行时极其高效的原因。

---

## 特征Trait

- 如果我们想定义一个文件系统，那么把该系统跟底层存储解耦是很重要的。文件操作主要包含四个：open 、write、read、close，这些操作可以发生在硬盘，可以发生在内存，还可以发生在网络 IO等等。总之如果你要为每一种情况都单独实现一套代码，那这种实现将过于繁杂，而且也没那个必要。
- 要解决上述问题，需要把这些行为抽象出来，就要使用 Rust 中的特征 trait 概念。如果学过其他语言，那么大概率你听说过接口，没错，特征跟接口很类似。
- 在之前的代码中，我们也多次见过特征的使用，例如 `#[derive(Debug)]`，它在我们定义的类型(struct)上自动派生 Debug 特征，接着可以使用 `println!("{:?}", x)` 打印这个类型；

---


- 如果不同的类型具有相同的行为，那么我们就可以定义一个特征，然后为这些类型实现该特征。定义特征是把一些方法组合在一起，目的是定义一个实现某些目标所必需的行为的集合。


## 返回值和错误处理


## 包和模块

- 二进制工程：让我们来创建一个二进制 Package：
```bash
cargo new my-project
```

---

- 创建一个库类型的 Package：
```bash
cargo new my-lib --lib
```

---

- Rust 社区已经为我们贡献了大量高质量的第三方包，你可以在 crates.io 或者 lib.rs 中检索和使用，从目前来说查找包更推荐 lib.rs，搜索功能更强大，内容展示也更加合理，但是下载依赖包还是得用crates.io。
- 你可以在网站上搜索 rand 包，看看它的文档使用方式是否和我们之前引入方式相一致：在网上找到想要的包，然后将你想要的包和版本信息写入到 Cargo.toml 中。

---

- 对于以下一行一行的引入方式：
```rust
use std::collections::HashMap;
use std::collections::BTreeMap;
use std::collections::HashSet;

//在大型项目中，使用这种方式来引入，可以减少大量 use 的使用：
use std::collections::{HashMap,BTreeMap,HashSet};

//对于下面的同时引入模块和模块中的项
use std::io;
use std::io::Write;

//可以使用 {} 的方式进行简化:
use std::io::{self, Write};
```


---

## 注释


```rust
/// `add_one` 将指定值加1
///
/// # Examples
///
/// ```
/// let arg = 5;
/// let answer = my_crate::add_one(arg);
///
/// assert_eq!(6, answer);
/// ```
pub fn add_one(x: i32) -> i32 {
    x + 1
}

/** `add_two` 将指定值加2

\```
let arg = 5;
let answer = my_crate::add_two(arg);

assert_eq!(7, answer);
\```
*/
pub fn add_two(x: i32) -> i32 {
    x + 2
}
```


---

- 除了函数、结构体等 Rust 项的注释，你还可以给包和模块添加注释，需要注意的是，这些注释要添加到包、模块的最上方！
- 与之前的任何注释一样，包级别的注释也分为两种：行注释 //! 和块注释 /*! ... */。
```rust
/*! lib包是world_hello二进制包的依赖包，
 里面包含了compute等有用模块 */

pub mod compute;
```

## 并发和并行


## 创建线程

- 使用 thread::spawn 可以创建线程：
```rust{.line-numbers}
use std::thread;
use std::time::Duration;

fn main() {
    thread::spawn(|| {
        for i in 1..10 {
            println!("hi number {} from the spawned thread!", i);
            thread::sleep(Duration::from_millis(1));
        }
    });

    for i in 1..5 {
        println!("hi number {} from the main thread!", i);
        thread::sleep(Duration::from_millis(1));
    }
}
```

- 如果多运行几次，你会发现好像每次输出会不太一样，因为：虽说线程往往是轮流执行的，但是这一点无法被保证！线程调度的方式往往取决于你使用的操作系统。总之，**千万不要依赖线程的执行顺序**。


## 等待子线程的结束

- 让主线程安全、可靠地等所有子线程完成任务后，再 kill self：
```rust{.line-numbers}
use std::thread;
use std::time::Duration;

fn main() {
    let handle = thread::spawn(|| {
        for i in 1..5 {
            println!("hi number {} from the spawned thread!", i);
            thread::sleep(Duration::from_millis(1));
        }
    });

    handle.join().unwrap();

    for i in 1..5 {
        println!("hi number {} from the main thread!", i);
        thread::sleep(Duration::from_millis(1));
    }
}
```


## 在线程闭包中使用 move

- 在闭包章节中，有讲过 move 关键字在闭包中的使用可以让该闭包拿走环境中某个值的所有权，同样地，你可以使用 move 来将所有权从一个线程转移到另外一个线程。

- 首先，来看看在一个线程中直接使用另一个线程中的数据会如何：
```rust
use std::thread;

fn main() {
    let v = vec![1, 2, 3];

    let handle = thread::spawn(|| {
        println!("Here's a vector: {:?}", v);
    });

    handle.join().unwrap();
}
```

- 大家要记住，线程的启动时间点和结束时间点是不确定的，因此存在一种可能，当主线程执行完， v 被释放掉时，新的线程很可能还没有结束甚至还没有被创建成功，此时新线程对 v 的引用立刻就不再合法！让我们使用 move 关键字拿走 v 的所有权即可：

```rust{.line-numbers}
use std::thread;

fn main() {
    let v = vec![1, 2, 3];

    let handle = thread::spawn(move || {
        println!("Here's a vector: {:?}", v);
    });

    handle.join().unwrap();

    // 下面代码会报错borrow of moved value: `v`
    // println!("{:?}",v);
}
```


## 线程是如何结束的

- 在系统编程中，操作系统提供了直接杀死线程的接口，简单粗暴，但是 Rust 并没有提供这样的接口，原因在于，粗暴地终止一个线程可能会导致资源没有释放、状态混乱等不可预期的结果，一向以安全自称的 Rust，自然不会砸自己的饭碗。

- 那么 Rust 中线程是如何结束的呢？答案很简单：线程的代码执行完，线程就会自动结束。但是如果线程中的代码不会执行完呢？那么情况可以分为两种进行讨论：
  - **IO阻塞读取**：绝大部分时间线程都处于阻塞的状态，因此虽然看上去是循环，CPU 占用其实很小，也是网络服务中最最常见的模型。
  - **忙循环**：线程的任务是一个循环，里面没有任何阻塞，包括休眠这种操作也没有，此时 CPU 很不幸的会被跑满，而且你如果没有设置终止条件，该线程将持续跑满一个 CPU 核心，并且不会被终止，直到 main 线程的结束。



## 线程屏障(Barrier)

- 在 Rust 中，可以使用 Barrier 让多个线程都执行到某个点后，才继续一起往后执行：

```rust
use std::sync::{Arc, Barrier};
use std::thread;

fn main() {
    let mut handles = Vec::with_capacity(6);
    let barrier = Arc::new(Barrier::new(6));

    for _ in 0..6 {
        let b = barrier.clone();
        handles.push(thread::spawn(move|| {
            println!("before wait");
            b.wait();
            println!("after wait");
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }
}
```

- 上面代码，我们在线程打印出 before wait 后增加了一个屏障，目的就是等所有的线程都打印出before wait后，各个线程再继续执行：
```txt
before wait
before wait
before wait
before wait
before wait
before wait
after wait
after wait
after wait
after wait
after wait
after wait
```

## 线程局部变量(Thread Local Variable)

- 使用 thread_local 宏可以初始化线程局部变量，然后在线程内部使用该变量的 with 方法获取变量值：

```rust
use std::cell::RefCell;
use std::thread;

thread_local!(static FOO: RefCell<u32> = RefCell::new(1));

FOO.with(|f| {
    assert_eq!(*f.borrow(), 1);
    *f.borrow_mut() = 2;
});

// 每个线程开始时都会拿到线程局部变量的FOO的初始值
let t = thread::spawn(move|| {
    FOO.with(|f| {
        assert_eq!(*f.borrow(), 1);
        *f.borrow_mut() = 3;
    });
});

// 等待线程完成
t.join().unwrap();

// 尽管子线程中修改为了3，我们在这里依然拥有main线程中的局部值：2
FOO.with(|f| {
    assert_eq!(*f.borrow(), 2);
});
```

## 只被调用一次的函数

- 有时，我们会需要某个函数在多线程环境下只被调用一次，例如初始化全局变量，无论是哪个线程先调用函数来初始化，都会保证全局变量只会被初始化一次，随后的其它线程调用就会忽略该函数：

```rust{.line-numbers}
use std::thread;
use std::sync::Once;

static mut VAL: usize = 0;
static INIT: Once = Once::new();

fn main() {
    let handle1 = thread::spawn(move || {
        INIT.call_once(|| {
            unsafe {
                VAL = 1;
            }
        });
    });

    let handle2 = thread::spawn(move || {
        INIT.call_once(|| {
            unsafe {
                VAL = 2;
            }
        });
    });

    handle1.join().unwrap();
    handle2.join().unwrap();

    println!("{}", unsafe { VAL });
}
```


## 线程间的消息传递


## 多发送者，单接收者

- 我们先来看看单发送者、单接收者的简单例子:
```rust{.line-numbers}
use std::sync::mpsc;
use std::thread;

fn main() {
    // 创建一个消息通道, 返回一个元组：(发送者，接收者)
    let (tx, rx) = mpsc::channel();

    // 创建线程，并发送消息
    thread::spawn(move || {
        // 发送一个数字1, send方法返回Result<T,E>，通过unwrap进行快速错误处理
        tx.send(1).unwrap();

        // 下面代码将报错，因为编译器自动推导出通道传递的值是i32类型，那么Option<i32>类型将产生不匹配错误
        // tx.send(Some(1)).unwrap()
    });

    // 在主线程中接收子线程发送的消息并输出
    println!("receive {}", rx.recv().unwrap());
}
```

---

- 除了上述recv方法，还可以使用try_recv尝试接收一次消息，该方法并不会阻塞线程，当通道中没有消息时，它会立刻返回一个错误：
```rust{.line-numbers}
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        tx.send(1).unwrap();
    });

    println!("receive {:?}", rx.try_recv());
}
```


# rust练手作业

## 实现一个线程安全的链表

- Arc是一种具有线程安全引用计数的类型。Mutex可以和Arc结合使用，以提供对共享数据的并发访问。下面是一些示例代码。在下面的代码中，我们创建了一个Mutex实例及其Arc的实例。然后，我们使用Arc的clone方法创建多个指向Mutex的引用，并在每个线程中使用被保护的变量。最后，我们打印结果。
```rust
use std::sync::{Mutex, Arc};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();

            *num += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Result: {}", *counter.lock().unwrap());
}
```

















# rustc应用



# cargo应用






# buttom







