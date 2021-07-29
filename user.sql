
--
-- Database: `speech_db`
--


CREATE TABLE `user` (
  `pid` int(11) NOT NULL,
  `fname` varchar(20) NOT NULL,
  `lname` varchar(20) NOT NULL,
  `ph_no` bigint(10) NOT NULL,
  `pswd` varchar(20) NOT NULL,
  `age` int(5) NOT NULL,
  `gender` enum('Female','Male') NOT NULL,
  `email` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`pid`, `fname`, `lname`, `ph_no`, `pswd`, `age`, `gender`, `email`) VALUES
(2, 'krishna', 'radha', 101010101, 'hello', 23, 'Female', 'hello@gmail.com'),
(4, 'oijeofj', 'ofno', 2222222222, 'hi', 22, 'Female', 'oeif@gmail.com');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`pid`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `pid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;
COMMIT;

